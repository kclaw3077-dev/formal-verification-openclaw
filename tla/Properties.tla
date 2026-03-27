------------------------------- MODULE Properties -------------------------------
(*
  Safety and Liveness properties for the SRE Infrastructure model.

  These are the invariants and temporal properties that the
  Formal Verification Gate checks before allowing Agent operations.
*)

EXTENDS SREInfrastructure

CONSTANTS
    CacheHitRateMin     \* Minimum acceptable cache hit rate (e.g. 50)

-----------------------------------------------------------------------------
(*  SAFETY PROPERTIES (Invariants - must hold in every reachable state) *)

\* Property 1: No Circular Dependencies
\* The dependency graph must always be a DAG.
\* Violation example: OrderSvc -> PaySvc -> OrderSvc (refund path)
NoCyclicDependencies ==
    ~HasCycle(dependencies)

\* Property 2: Minimum Redundancy on Critical Path
\* Every service on the critical path must have at least MinSafeReplicas.
\* This ensures no single point of failure on the critical path.
MinimumRedundancy ==
    \A s \in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]

\* Property 3: No Split-Brain
\* Database writes must come from exactly one region at a time.
\* "both" means split-brain - two regions accepting writes simultaneously.
NoSplitBrain ==
    dbWriteRegion \in Regions  \* not "both"

\* Property 4: Traffic-Write Consistency
\* The region receiving traffic should be the region accepting DB writes,
\* OR writes should have already been switched before traffic.
\* This prevents reading stale data.
TrafficWriteConsistency ==
    activeRegion = dbWriteRegion

\* Property 5: Availability Floor (No-Degradation Principle)
\* The effective capacity of every critical-path service must remain
\* above 50% of its configured replica count at all times.
\* This formalizes "no operation should degrade service availability."
AvailabilityFloor ==
    \A s \in CriticalPath :
        EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]

\* Property 6: Blast Radius Bound
\* If any single service goes down, at most 2 other services
\* should be directly affected. This limits failure propagation.
BlastRadiusBound ==
    \A s \in Services :
        Cardinality({t \in Services : s \in dependencies[t]}) <= 2

\* Property 7: No Simultaneous Updates on Backup Pairs
\* Services that are on the same dependency chain should not both
\* be in "deploying" state simultaneously.
NoSimultaneousUpdatesOnChain ==
    \A s \in Services : \A t \in dependencies[s] :
        ~(\E r1, r2 \in Regions :
            serviceState[s][r1] = "deploying" /\ serviceState[t][r2] = "deploying")

\* Property 8: Cache Hit Rate Floor
\* Every cached service must maintain a cache hit rate above the minimum threshold.
\* A low hit rate indicates a cache miss storm that could overwhelm the database.
CacheHitRateFloor ==
    \A s \in CachedServices : cacheHitRate[s] >= CacheHitRateMin

\* Combined Safety Invariant
SafetyInvariant ==
    /\ NoCyclicDependencies
    /\ MinimumRedundancy
    /\ NoSplitBrain
    /\ AvailabilityFloor
    /\ NoSimultaneousUpdatesOnChain
    /\ CacheHitRateFloor

-----------------------------------------------------------------------------
(*  LIVENESS PROPERTIES (Temporal - something good eventually happens) *)

\* Every deploying service eventually returns to running
EventualRecovery ==
    \A s \in Services : \A r \in Regions :
        serviceState[s][r] = "deploying" ~> serviceState[s][r] = "running"

\* If traffic is switched, DB writes eventually follow
EventualWriteConsistency ==
    (activeRegion # dbWriteRegion) ~> (activeRegion = dbWriteRegion)

=============================================================================
