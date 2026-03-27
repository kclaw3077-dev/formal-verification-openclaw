--------------------------- MODULE SREInfrastructure ---------------------------
(*
  Core model of an SRE microservice infrastructure.

  Models:
    - Services with replica counts and health states
    - Dependency graph between services (including redis cache layer)
    - Multi-region deployment
    - Agent operations as state transitions
    - Redis cache hit rate tracking per service
*)

EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
    Services,           \* Set of service names
    Regions,            \* Set of region names
    MaxReplicas,        \* Maximum replicas per service
    MinSafeReplicas,    \* Minimum replicas for safety (per service)
    CriticalPath,       \* Set of services on the critical path
    SLAMaxDowntimeSteps \* Maximum steps a critical service can be unavailable

\* Services that use a redis cache layer
CachedServices == {"user-svc"}

VARIABLES
    replicas,           \* replicas[s][r] = number of running replicas of service s in region r
    dependencies,       \* dependencies[s] = set of services that s depends on
    serviceState,       \* serviceState[s][r] \in {"running", "deploying", "degraded", "down"}
    activeRegion,       \* activeRegion = the region currently serving traffic
    dbWriteRegion,      \* dbWriteRegion = the region accepting database writes ("both" = split-brain)
    pendingOps,         \* pendingOps = sequence of pending agent operations
    opHistory,          \* opHistory = sequence of completed operations
    stepCount,          \* stepCount = global step counter for temporal reasoning
    cacheHitRate        \* cacheHitRate[s] = cache hit percentage (0-100) for service s

vars == <<replicas, dependencies, serviceState, activeRegion,
          dbWriteRegion, pendingOps, opHistory, stepCount, cacheHitRate>>

-----------------------------------------------------------------------------
(*  Helper operators *)

\* Total replicas of a service across all regions
TotalReplicas(s) ==
    LET regionSet == {r \in Regions : TRUE}
    IN  LET f[r \in Regions] == replicas[s][r]
        IN  LET Sum[S \in SUBSET Regions] ==
                IF S = {} THEN 0
                ELSE LET x == CHOOSE x \in S : TRUE
                     IN  f[x] + Sum[S \ {x}]
            IN Sum[Regions]

\* Is service s healthy (at least MinSafe replicas running)?
IsHealthy(s) ==
    TotalReplicas(s) >= MinSafeReplicas[s]

\* Effective capacity of a service (considering deploying state reduces capacity)
EffectiveCapacity(s) ==
    LET running == {r \in Regions : serviceState[s][r] = "running"}
        deploying == {r \in Regions : serviceState[s][r] = "deploying"}
    IN  LET runCap[S \in SUBSET Regions] ==
            IF S = {} THEN 0
            ELSE LET x == CHOOSE x \in S : TRUE
                 IN  replicas[s][x] + runCap[S \ {x}]
        IN  LET depCap[S \in SUBSET Regions] ==
            IF S = {} THEN 0
            ELSE LET x == CHOOSE x \in S : TRUE
                 IN  (replicas[s][x] \div 2) + depCap[S \ {x}]  \* deploying = half capacity
        IN runCap[running] + depCap[deploying]

\* Can service s serve requests? (considering its dependencies)
CanServe(s) ==
    /\ IsHealthy(s)
    /\ \A dep \in dependencies[s] : IsHealthy(dep)

\* All services on critical path can serve
CriticalPathAvailable ==
    \A s \in CriticalPath : CanServe(s)

\* Transitive closure of dependencies - detect cycles
RECURSIVE ReachableFrom(_,_,_)
ReachableFrom(s, visited, deps) ==
    LET directDeps == deps[s] \ visited
    IN  directDeps \cup
        UNION {ReachableFrom(d, visited \cup directDeps, deps) : d \in directDeps}

HasCycle(deps) ==
    \E s \in Services : s \in ReachableFrom(s, {}, deps)

\* Is the cache for service s healthy? (hit rate above 50%)
CacheHealthy(s) == cacheHitRate[s] >= 50

-----------------------------------------------------------------------------
(*  Initial State *)

Init ==
    /\ replicas = [s \in Services |-> [r \in Regions |->
        IF s = "database" THEN (IF r = "east" THEN 1 ELSE 2) ELSE 3]]
    /\ dependencies = [s \in Services |->
        CASE s = "gateway"   -> {"user-svc", "order-svc", "pay-svc"}
          [] s = "order-svc" -> {"inventory-svc", "pay-svc"}
          [] s = "pay-svc"   -> {"database"}
          [] s = "inventory-svc" -> {"database"}
          [] s = "user-svc"  -> {"database"}
          [] OTHER           -> {}]
    /\ serviceState = [s \in Services |-> [r \in Regions |-> "running"]]
    /\ activeRegion = "east"
    /\ dbWriteRegion = "east"
    /\ pendingOps = <<>>
    /\ opHistory = <<>>
    /\ stepCount = 0
    /\ cacheHitRate = [s \in Services |-> 99]

-----------------------------------------------------------------------------
(*  Agent Operations - State Transitions *)

\* Rolling update: temporarily reduces capacity
RollingUpdate(s, r) ==
    /\ serviceState[s][r] = "running"
    /\ serviceState' = [serviceState EXCEPT ![s][r] = "deploying"]
    /\ replicas' = replicas  \* replicas stay same, but effective capacity drops
    /\ UNCHANGED <<dependencies, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "rolling_update", service |-> s, region |-> r])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = Tail(pendingOps)

\* Complete update: service back to running
CompleteUpdate(s, r) ==
    /\ serviceState[s][r] = "deploying"
    /\ serviceState' = [serviceState EXCEPT ![s][r] = "running"]
    /\ UNCHANGED <<replicas, dependencies, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "complete_update", service |-> s, region |-> r])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Scale down: reduce replicas
ScaleDown(s, r, n) ==
    /\ replicas[s][r] > 0
    /\ n > 0
    /\ n <= replicas[s][r]
    /\ replicas' = [replicas EXCEPT ![s][r] = replicas[s][r] - n]
    /\ UNCHANGED <<dependencies, serviceState, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "scale_down", service |-> s, region |-> r, amount |-> n])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Scale up: increase replicas
ScaleUp(s, r, n) ==
    /\ n > 0
    /\ replicas[s][r] + n <= MaxReplicas
    /\ replicas' = [replicas EXCEPT ![s][r] = replicas[s][r] + n]
    /\ UNCHANGED <<dependencies, serviceState, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "scale_up", service |-> s, region |-> r, amount |-> n])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Add dependency: s now depends on target
AddDependency(s, target) ==
    /\ target \notin dependencies[s]
    /\ s # target
    /\ dependencies' = [dependencies EXCEPT ![s] = dependencies[s] \cup {target}]
    /\ UNCHANGED <<replicas, serviceState, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "add_dep", from |-> s, to |-> target])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Region failover step 1: switch DNS (traffic region changes)
SwitchTraffic(targetRegion) ==
    /\ activeRegion # targetRegion
    /\ activeRegion' = targetRegion
    /\ UNCHANGED <<replicas, dependencies, serviceState, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "switch_traffic", to |-> targetRegion])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Region failover step 2: switch DB writes
SwitchDBWrites(targetRegion) ==
    /\ dbWriteRegion # targetRegion
    /\ dbWriteRegion' = targetRegion
    /\ UNCHANGED <<replicas, dependencies, serviceState, activeRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "switch_db_writes", to |-> targetRegion])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

\* Failure injection: a replica crashes (models real-world faults)
ReplicaFailure(s, r) ==
    /\ replicas[s][r] > 0
    /\ replicas' = [replicas EXCEPT ![s][r] = replicas[s][r] - 1]
    /\ serviceState' = [serviceState EXCEPT ![s][r] =
        IF replicas[s][r] - 1 = 0 THEN "down" ELSE serviceState[s][r]]
    /\ UNCHANGED <<dependencies, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "replica_failure", service |-> s, region |-> r])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = pendingOps

\* Redis cache burst: cache miss storm drops hit rate to 12%
RedisCacheBurst(s) ==
    /\ s \in CachedServices
    /\ cacheHitRate[s] >= 50  \* only trigger if cache is currently healthy
    /\ cacheHitRate' = [cacheHitRate EXCEPT ![s] = 12]
    /\ UNCHANGED <<replicas, dependencies, serviceState, activeRegion, dbWriteRegion>>
    /\ opHistory' = Append(opHistory, [op |-> "redis_cache_burst", service |-> s])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = pendingOps

\* Rate limit a service in a specific region
RateLimitService(s, r) ==
    /\ serviceState[s][r] = "running"
    /\ serviceState' = [serviceState EXCEPT ![s][r] = "degraded"]
    /\ UNCHANGED <<replicas, dependencies, activeRegion, dbWriteRegion, cacheHitRate>>
    /\ opHistory' = Append(opHistory, [op |-> "rate_limit", service |-> s, region |-> r])
    /\ stepCount' = stepCount + 1
    /\ pendingOps' = IF pendingOps = <<>> THEN <<>> ELSE Tail(pendingOps)

-----------------------------------------------------------------------------
(*  Next state relation *)

Next ==
    \/ \E s \in Services, r \in Regions : RollingUpdate(s, r)
    \/ \E s \in Services, r \in Regions : CompleteUpdate(s, r)
    \/ \E s \in Services, r \in Regions, n \in 1..MaxReplicas : ScaleDown(s, r, n)
    \/ \E s \in Services, r \in Regions, n \in 1..MaxReplicas : ScaleUp(s, r, n)
    \/ \E s \in Services, t \in Services : AddDependency(s, t)
    \/ \E r \in Regions : SwitchTraffic(r)
    \/ \E r \in Regions : SwitchDBWrites(r)
    \/ \E s \in Services, r \in Regions : ReplicaFailure(s, r)
    \/ \E s \in Services : RedisCacheBurst(s)
    \/ \E s \in Services, r \in Regions : RateLimitService(s, r)

Spec == Init /\ [][Next]_vars

=============================================================================
