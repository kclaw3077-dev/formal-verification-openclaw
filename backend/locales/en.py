"""English locale — all user-facing scenario text."""

SCENARIOS = {
    # ── Scenario 1 ──────────────────────────────────────────────────────────
    "scenario-1": {
        "title": "SLO Conflict Detection",
        "subtitle": "Pre-event specification validation",
        "phase": "① Realizability Check",
        "description": (
            "Before a major sales event, the SRE team defines three SLOs for the "
            "payment path: 99.99% availability, P99 latency under 200ms, and strong "
            "consistency between pay-svc and database. Realizability Check discovers "
            "these three specifications CANNOT be simultaneously satisfied under the "
            "current dual-AZ deployment."
        ),
        "constraints": [
            {
                "name": "Availability_99_99",
                "expression": "Availability(pay-svc) >= 0.9999",
                "threshold": "99.99%",
                "description": "Payment service availability must exceed 99.99%",
            },
            {
                "name": "LatencyP99_200ms",
                "expression": "P99Latency(pay-svc) <= 200",
                "threshold": "200ms",
                "description": "Payment path P99 latency must stay below 200ms",
            },
            {
                "name": "StrongConsistency",
                "expression": 'ConsistencyLevel(pay-svc, database) = "strong"',
                "threshold": "Strong",
                "description": "Synchronous replication between pay-svc and database",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "SwitchTraffic", "SwitchDBWrites"],
                "relevant_section": "Multi-region service model with failover operations",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "AvailabilityFloor"],
                "relevant_section": "Consistency and availability invariants",
            },
        },
        "steps": {
            1: {
                "title": "Define Payment Path SLOs",
                "description": (
                    "SRE team defines three simultaneous requirements for the payment "
                    "critical path: 99.99% availability, P99 latency under 200ms, and "
                    "strong consistency. Under dual-AZ deployment, strong consistency "
                    "requires synchronous cross-AZ replication. When one AZ fails, "
                    "synchronous replication adds latency that pushes P99 beyond 200ms, "
                    "forcing availability degradation below 99.99%."
                ),
                "agent_action": "define_slo(availability=99.99%, latency_p99<200ms, consistency=strong)",
            },
            2: {
                "title": "Relax Specifications",
                "description": (
                    "Adjust strong consistency to eventual consistency with bounded "
                    "staleness for non-critical reads. Payment writes keep strong "
                    "consistency with relaxed P99 to 500ms. Non-critical query path "
                    "uses eventual consistency with P99 under 200ms. Re-check confirms "
                    "the relaxed specification set is realizable."
                ),
                "agent_action": "relax_spec(critical_path=strong+500ms, query_path=eventual+200ms)",
            },
        },
        "violations": {
            "RealizabilityConflict": (
                "Under dual-AZ deployment, when east-AZ fails, synchronous replication "
                "to west-AZ adds 150-300ms latency. This makes P99<200ms impossible "
                "while maintaining strong consistency and 99.99% availability "
                "simultaneously. This is a manifestation of the CAP theorem on the "
                "specific deployment topology."
            ),
        },
        "trace": {
            1: "Initial state: Dual-AZ deployment, east is primary, synchronous replication enabled",
            2: "East-AZ database primary experiences network partition",
            3: (
                "Strong consistency requires west-AZ acknowledgment before write commit "
                "\u2192 adds 150-300ms cross-AZ latency \u2192 P99 exceeds 200ms \u2192 must reject "
                "writes to maintain latency SLO \u2192 availability drops below 99.99%"
            ),
        },
        "counterexample": {
            1: "state: {east: primary, west: replica, sync_replication: true, all_healthy: true} \u2014 SLOs satisfied",
            2: "event: east-AZ network partition \u2192 sync replication latency increases to 280ms",
            3: (
                "conflict: P99=280ms > 200ms threshold. To maintain P99<200ms, must "
                "reject slow writes \u2192 availability=99.91% < 99.99%. Three SLOs form "
                "an impossible triangle under this topology."
            ),
        },
        "tla_spec": (
            "---- MODULE RealizabilityCheck ----\n"
            "EXTENDS Naturals, FiniteSets\n"
            "CONSTANTS East, West\n"
            "VARIABLES activeAZ, syncReplication, p99Latency, availability\n\n"
            "Regions == {East, West}\n\n"
            "TypeOK ==\n"
            "    /\\ activeAZ \\in Regions\n"
            "    /\\ syncReplication \\in BOOLEAN\n"
            "    /\\ p99Latency \\in 0..1000\n"
            "    /\\ availability \\in 0..10000  \\* basis points\n\n"
            "SLO_Availability  == availability >= 9999\n"
            "SLO_LatencyP99    == p99Latency <= 200\n"
            "SLO_StrongConsist == syncReplication = TRUE\n\n"
            "\\* Under partition, sync replication adds cross-AZ latency\n"
            "EastPartition ==\n"
            "    /\\ activeAZ = East\n"
            "    /\\ syncReplication = TRUE\n"
            "    /\\ p99Latency' = 280         \\* cross-AZ sync cost\n"
            "    /\\ availability' = 9991       \\* must reject slow writes\n"
            "    /\\ UNCHANGED <<activeAZ, syncReplication>>\n\n"
            "\\* The conjunction is unsatisfiable under partition\n"
            "AllSLOs == SLO_Availability /\\ SLO_LatencyP99 /\\ SLO_StrongConsist\n\n"
            "\\* THEOREM: EastPartition => ~AllSLOs'\n"
            "====\n"
        ),
    },

    # ── Scenario 2 ──────────────────────────────────────────────────────────
    "scenario-2": {
        "title": "Elastic Strategy Synthesis",
        "subtitle": "Auto-generate correct scaling controller",
        "phase": "\u2461 Reactive Synthesis",
        "description": (
            "Based on corrected specifications from Case 1, Reactive Synthesis "
            "automatically generates a traffic scheduling and elastic scaling "
            "controller. Instead of manually writing SOPs, the synthesizer produces "
            "a correct-by-construction state machine that handles peak traffic "
            "patterns, discovering constraints that humans would likely miss."
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "Critical path services must maintain at least 66% effective throughput",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "varies",
                "description": "Each critical service maintains minimum safe replicas",
            },
            {
                "name": "NoSimultaneousUpdatesOnChain",
                "expression": "\\A s,t : s->t => ~(deploying(s) /\\ deploying(t))",
                "threshold": "N/A",
                "description": "Dependent services cannot both be deploying simultaneously",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["EffectiveCapacity", "RollingUpdate", "ScaleUp", "ScaleDown"],
                "relevant_section": "Capacity model and scaling operations",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "NoSimultaneousUpdatesOnChain"],
                "relevant_section": "Safety constraints for the synthesized controller",
            },
        },
        "steps": {
            1: {
                "title": "Input Specifications to Synthesizer",
                "description": (
                    "Provide the environment model (traffic range 1x-10x, single AZ "
                    "max pod count, AZ failure probability) and safety specifications "
                    "(AvailabilityFloor, MinimumRedundancy, NoSimultaneousUpdatesOnChain) "
                    "to the Reactive Synthesis engine."
                ),
                "agent_action": (
                    "synthesize(env_model={traffic:1x-10x, max_pods:20}, "
                    "safety_specs=[AvailabilityFloor, MinimumRedundancy, "
                    "NoSimultaneousUpdatesOnChain])"
                ),
            },
            2: {
                "title": "Discover Mutual Exclusion Constraint",
                "description": (
                    "The synthesizer discovers a critical constraint through "
                    "game-theoretic analysis: when traffic exceeds 8x normal, scaling "
                    "and rolling update operations are mutually exclusive. At 8x "
                    "traffic, EffectiveCapacity during rolling update drops to exactly "
                    "the AvailabilityFloor boundary. Any concurrent scaling operation "
                    "would temporarily reduce capacity further, violating the floor."
                ),
                "agent_action": "synthesis_result: guard(traffic > 8x \u2192 mutex(scale, rolling_update))",
            },
            3: {
                "title": "Generate Complete Controller",
                "description": (
                    "The synthesizer outputs the complete state machine with all "
                    "guards, including: inventory-svc must scale before order-svc "
                    "(bottleneck-first ordering), single-AZ failover must switch DB "
                    "writes before traffic (anti-split-brain), and the 8x traffic "
                    "mutual exclusion guard. The controller is correct-by-construction."
                ),
                "agent_action": "output: StateMachine(states=4, transitions=12, guards=6)",
            },
        },
        "violations": {},
        "trace": {
            1: "Synthesis engine explores environment model: traffic \u2208 {1x, 2x, 4x, 8x, 10x}",
            2: "At traffic=8x: EffectiveCapacity during rolling_update = MinSafeReplicas \u00d7 0.66 \u2014 exactly at boundary",
            3: "At traffic=8x + concurrent scale_up: temporary capacity dip during pod initialization \u2192 EffectiveCapacity < AvailabilityFloor",
            4: "Synthesizer adds guard: traffic_multiplier <= 8 \u2228 \u00acrolling_update_in_progress",
        },
        "counterexample": {},
        "tla_spec": (
            "---- MODULE SynthesizedController ----\n"
            "EXTENDS Naturals\n"
            "CONSTANTS MaxPods, CriticalPath\n"
            "VARIABLES traffic, replicas, controllerState, rollingUpdate\n\n"
            "TrafficLevels == {1, 2, 4, 8, 10}\n"
            "States == {\"idle\", \"scaling\", \"updating\", \"failover\"}\n\n"
            "EffectiveCapacity(s) ==\n"
            "    IF rollingUpdate[s] THEN replicas[s] * 2 \\div 3\n"
            "    ELSE replicas[s]\n\n"
            "\\* Guard discovered by synthesis: mutual exclusion at high traffic\n"
            "CanRollingUpdate(s) ==\n"
            "    /\\ traffic <= 8\n"
            "    /\\ controllerState \\notin {\"scaling\"}\n"
            "    /\\ \\A t \\in CriticalPath :\n"
            "         t # s => ~rollingUpdate[t]  \\* chain exclusion\n\n"
            "CanScale(s) ==\n"
            "    /\\ replicas[s] < MaxPods\n"
            "    /\\ traffic <= 8 \\/ ~rollingUpdate[s]\n\n"
            "\\* Bottleneck-first ordering: scale downstream before upstream\n"
            "ScaleOrder(s, t) ==\n"
            "    s \\in CriticalPath /\\ t \\in CriticalPath =>\n"
            "        (replicas[s] >= replicas[t] \\/ controllerState = \"scaling\")\n\n"
            "SafetyInvariant ==\n"
            "    \\A s \\in CriticalPath :\n"
            "        EffectiveCapacity(s) * 2 >= replicas[s]\n"
            "====\n"
        ),
    },

    # ── Scenario 3 ──────────────────────────────────────────────────────────
    "scenario-3": {
        "title": "Change Verification \u2014 Emergency Hotfix",
        "subtitle": "Pre-deployment safety check catches compound failure",
        "phase": "\u2462 Runtime Verification",
        "description": (
            "One day before the major sales event, a critical concurrency bug is "
            "discovered in inventory-svc stock deduction logic. The service has been "
            "pre-scaled to 4 replicas (2 east, 2 west) for the event. The Agent "
            "proposes a standard rolling update, but BMC discovers a dangerous "
            "compound failure scenario."
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "Critical path services must maintain at least 66% effective throughput",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "varies",
                "description": "Each critical service maintains minimum safe replicas",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["RollingUpdate", "EffectiveCapacity", "ReplicaFailure"],
                "relevant_section": "Rolling update capacity model with fault injection",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "MinimumRedundancy"],
                "relevant_section": "Throughput and redundancy safety floors",
            },
        },
        "steps": {
            1: {
                "title": "Agent Proposes Rolling Update",
                "description": (
                    "Agent proposes rolling update for inventory-svc (4 replicas: "
                    "2 east, 2 west). BMC explores all reachable states within 3 steps. "
                    "At step 2, when east-pod-1 is being updated (capacity halved), if "
                    "order-svc east-pod-2 simultaneously enters GC pause (degraded "
                    "state), the critical chain gateway\u2192order-svc\u2192inventory-svc "
                    "effective throughput drops to 50%, below the 66% AvailabilityFloor."
                ),
                "agent_action": "rolling_update(service=inventory-svc, strategy=one-at-a-time)",
            },
            2: {
                "title": "Adjusted Plan: Scale First, Then Update",
                "description": (
                    "Agent adjusts: first scale inventory-svc to 6 replicas (3 east, "
                    "3 west), then perform rolling update. With 6 replicas, even during "
                    "update + GC pause compound scenario, effective throughput stays at "
                    "66% \u2014 exactly at the safety boundary. BMC verifies all reachable "
                    "states within 3 steps pass."
                ),
                "agent_action": "scale_up(inventory-svc, to=6) && rolling_update(inventory-svc)",
            },
        },
        "violations": {
            "AvailabilityFloor": (
                "During rolling update step 2, with east-pod-1 deploying (50% east "
                "capacity) and order-svc east-pod-2 in GC pause (degraded), the "
                "critical chain gateway\u2192order-svc\u2192inventory-svc drops to 50% "
                "effective throughput, below the 66% AvailabilityFloor."
            ),
        },
        "trace": {
            1: "Initial: inventory-svc has 4 replicas (2E/2W), all running. Chain throughput = 100%",
            2: "Step 1: rolling_update starts on inventory-svc east-pod-1 \u2192 east capacity = 1 running + 1 deploying (50%) \u2192 chain throughput = 75%",
            3: "Step 2: order-svc east-pod-2 enters GC pause (degraded) \u2192 order-svc east effective = 66% \u2192 combined chain throughput = 75% \u00d7 66% \u2248 50% < 66% AvailabilityFloor \u2717",
        },
        "counterexample": {
            1: "state: {inventory-svc: 2E/2W running, order-svc: 3E/3W running} \u2014 throughput=100%",
            2: "action: rolling_update(inventory-svc, east-pod-1) \u2192 {inventory-svc east: 1 running + 1 deploying} \u2014 throughput=75%",
            3: "environment: order-svc east-pod-2 GC pause \u2192 {order-svc east: 2 running + 1 degraded} \u2014 chain throughput=50% < 66% \u2717 VIOLATED",
        },
        "tla_spec": (
            "---- MODULE RollingUpdateBMC ----\n"
            "EXTENDS Naturals\n"
            "CONSTANTS Services, Regions, East, West\n"
            "VARIABLES serviceState, replicaCounts, chainThroughput\n\n"
            "EffectiveCapacity(s, r) ==\n"
            "    LET running  == replicaCounts[s][r][\"running\"]\n"
            "        deploying == replicaCounts[s][r][\"deploying\"]\n"
            "        degraded  == replicaCounts[s][r][\"degraded\"]\n"
            "    IN running + (deploying * 50 \\div 100) + (degraded * 66 \\div 100)\n\n"
            "ChainThroughput(chain) ==\n"
            "    \\* Minimum effective capacity across all services in the chain\n"
            "    100  \\* placeholder: product of per-service capacities\n\n"
            "RollingUpdate(s, r) ==\n"
            "    /\\ replicaCounts'[s][r][\"running\"]  = replicaCounts[s][r][\"running\"] - 1\n"
            "    /\\ replicaCounts'[s][r][\"deploying\"] = replicaCounts[s][r][\"deploying\"] + 1\n\n"
            "GCPause(s, r) ==\n"
            "    /\\ replicaCounts'[s][r][\"running\"]  = replicaCounts[s][r][\"running\"] - 1\n"
            "    /\\ replicaCounts'[s][r][\"degraded\"] = replicaCounts[s][r][\"degraded\"] + 1\n\n"
            "AvailabilityFloor ==\n"
            "    \\A s \\in Services :\n"
            "        EffectiveCapacity(s, East) + EffectiveCapacity(s, West) >= 66\n\n"
            "\\* BMC depth 3: Init -> RollingUpdate -> GCPause -> check\n"
            "====\n"
        ),
    },

    # ── Scenario 4 ──────────────────────────────────────────────────────────
    "scenario-4": {
        "title": "Fault Interception \u2014 Failover Split-Brain",
        "subtitle": "Preventing split-brain during database failover",
        "phase": "\u2462 Runtime Verification",
        "description": (
            "During peak traffic on sales day, the east-region database primary "
            "experiences latency spikes (50% of requests timing out). The synthesized "
            "controller from Case 2 triggers a failover. The Agent generates a 2-step "
            "plan: switch traffic to west, then switch DB writes to west. BMC detects "
            "a split-brain risk in this ordering."
        ),
        "constraints": [
            {
                "name": "TrafficWriteConsistency",
                "expression": "activeRegion = dbWriteRegion",
                "threshold": "must match",
                "description": "Traffic region and DB write region must be the same to prevent split-brain",
            },
            {
                "name": "NoSplitBrain",
                "expression": "dbWriteRegion \\in Regions",
                "threshold": "single region",
                "description": "Database writes must come from exactly one region",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["SwitchTraffic", "SwitchDBWrites", "activeRegion", "dbWriteRegion"],
                "relevant_section": "Multi-region failover operations",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "NoSplitBrain"],
                "relevant_section": "Consistency invariants for failover",
            },
        },
        "steps": {
            1: {
                "title": "Agent Plan: Switch Traffic First",
                "description": (
                    "Agent generates failover plan: Step A \u2014 SwitchTraffic(west), "
                    "Step B \u2014 SwitchDBWrites(west). BMC checks all reachable states "
                    "across this 2-step plan. After Step A completes but before Step B "
                    "executes, activeRegion=west but dbWriteRegion=east. West-region "
                    "pay-svc receives traffic and attempts writes, but writes are routed "
                    "to the east-region database (still the write primary). Meanwhile, "
                    "the east database is recovering and may accept some writes, "
                    "creating a split-brain window."
                ),
                "agent_action": "failover_plan: [SwitchTraffic(west), SwitchDBWrites(west)]",
            },
            2: {
                "title": "Corrected Plan: Switch Writes First",
                "description": (
                    "Agent reverses the order: Step A \u2014 SwitchDBWrites(west), Step B \u2014 "
                    "SwitchTraffic(west). BMC verifies: after Step A, dbWriteRegion=west, "
                    "activeRegion=east \u2014 traffic still goes to east, which forwards "
                    "writes to west (safe, just slower). After Step B, both regions "
                    "align. No split-brain window exists."
                ),
                "agent_action": "failover_plan: [SwitchDBWrites(west), SwitchTraffic(west)]",
            },
        },
        "violations": {
            "TrafficWriteConsistency": (
                "After SwitchTraffic(west) but before SwitchDBWrites(west), "
                "activeRegion=west \u2260 dbWriteRegion=east. Traffic arrives at "
                "west-region services which attempt writes to the east database. "
                "A 30-second window exists where both regions may accept writes, "
                "causing data inconsistency."
            ),
        },
        "trace": {
            1: "Initial: activeRegion=east, dbWriteRegion=east, database-east experiencing latency",
            2: "Action: SwitchTraffic(west) \u2192 activeRegion=west, dbWriteRegion=east \u2014 MISMATCH",
            3: "Window: west pay-svc receives orders \u2192 writes go to east DB (slow/failing) \u2192 timeouts \u2192 retries may hit west DB replica \u2192 split-brain",
        },
        "counterexample": {
            1: "state: {activeRegion: east, dbWriteRegion: east} \u2014 consistent \u2713",
            2: "action: SwitchTraffic(west) \u2192 {activeRegion: west, dbWriteRegion: east} \u2014 TrafficWriteConsistency VIOLATED \u2717",
            3: "consequence: west pay-svc writes to east DB (300ms latency + 50% timeout) while east DB may also accept local writes during recovery",
        },
        "tla_spec": (
            "---- MODULE FailoverOrdering ----\n"
            "EXTENDS Naturals\n"
            "CONSTANTS East, West\n"
            "VARIABLES activeRegion, dbWriteRegion, dbLatency\n\n"
            "Regions == {East, West}\n"
            "vars == <<activeRegion, dbWriteRegion, dbLatency>>\n\n"
            "Init ==\n"
            "    /\\ activeRegion = East\n"
            "    /\\ dbWriteRegion = East\n"
            "    /\\ dbLatency = 300  \\* east DB degraded\n\n"
            "SwitchTraffic(r) ==\n"
            "    /\\ activeRegion' = r\n"
            "    /\\ UNCHANGED <<dbWriteRegion, dbLatency>>\n\n"
            "SwitchDBWrites(r) ==\n"
            "    /\\ dbWriteRegion' = r\n"
            "    /\\ dbLatency' = IF r = West THEN 5 ELSE dbLatency\n"
            "    /\\ UNCHANGED activeRegion\n\n"
            "\\* Unsafe plan: traffic first\n"
            "UnsafePlan == SwitchTraffic(West) \\/ SwitchDBWrites(West)\n\n"
            "TrafficWriteConsistency == activeRegion = dbWriteRegion\n"
            "NoSplitBrain == dbWriteRegion \\in Regions\n\n"
            "\\* BMC finds: SwitchTraffic(West) -> TrafficWriteConsistency violated\n"
            "\\* Safe order: SwitchDBWrites(West) then SwitchTraffic(West)\n"
            "====\n"
        ),
    },

    # ── Scenario 5 ──────────────────────────────────────────────────────────
    "scenario-5": {
        "title": "Fault Retrospective & Feedback Loop",
        "subtitle": "From incident analysis to specification evolution",
        "phase": "\u2463 Post-Incident \u2192 \u2460",
        "description": (
            "After the sales event, a real cascading failure is analyzed: a "
            "promotional popup caused 10x query surge on user-svc, leading to Redis "
            "cache hot-key eviction, user-svc cache miss storm hitting the database, "
            "connection pool exhaustion, and full-chain 5xx errors. BMC reverse "
            "analysis traces the shortest fault path and generates new specifications "
            "that feed back to Phase \u2460."
        ),
        "constraints": [
            {
                "name": "CacheHitRateFloor",
                "expression": "\\A s \\in CachedServices : cacheHitRate[s] >= 50",
                "threshold": "50%",
                "description": "Cache-dependent services must maintain minimum 50% hit rate",
            },
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "Critical path services must maintain at least 66% effective throughput",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "varies",
                "description": "Each critical service maintains minimum safe replicas",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["RedisCacheBurst", "cacheHitRate", "CacheHealthy", "ReplicaFailure"],
                "relevant_section": "Cache failure model and fault injection",
            },
            "Properties.tla": {
                "defines": ["CacheHitRateFloor", "AvailabilityFloor"],
                "relevant_section": "New cache health invariant discovered in retrospective",
            },
        },
        "steps": {
            1: {
                "title": "BMC Reverse: Trace Fault Path",
                "description": (
                    "Starting from the fault terminal state (full-chain 5xx), BMC "
                    "reverse searches backward to find the shortest path that reaches "
                    "this state. The result: only 3 steps are needed \u2014 (1) Redis "
                    "hot-key eviction drops cache hit rate to 12%, (2) user-svc falls "
                    "back to database for all queries, exhausting the connection pool, "
                    "(3) database becomes unavailable, causing order-svc and pay-svc "
                    "to fail, triggering full-chain 5xx. The root cause: no invariant "
                    "monitors cache health."
                ),
                "agent_action": "bmc_reverse(terminal_state=full_chain_5xx, max_depth=5)",
            },
            2: {
                "title": "Generate New Invariant",
                "description": (
                    "Based on the fault path analysis, a new safety invariant is "
                    "proposed: CacheHitRateFloor \u2014 all cache-dependent services must "
                    "maintain at least 50% cache hit rate. Additionally, a new fault "
                    "mode (CacheBurstEviction) and a new defensive operation "
                    "(RateLimitService) are added to the system model. BMC verifies "
                    "that with CacheHitRateFloor active, the 3-step fault path would "
                    "have been caught at step 1 (cache hit rate drop to 12% < 50%)."
                ),
                "agent_action": "propose_invariant(CacheHitRateFloor: cacheHitRate >= 50%)",
            },
            3: {
                "title": "Feed Back to Phase \u2460 \u2014 Re-check Realizability",
                "description": (
                    "The expanded specification set (original specs from Case 1 + "
                    "CacheHitRateFloor + CacheBurstEviction fault mode) is checked "
                    "for realizability. Result: REALIZABLE. The new specs can be "
                    "simultaneously satisfied. The controller from Case 2 can be "
                    "re-synthesized to include cache health as a pre-condition for "
                    "scaling decisions. The feedback loop is complete."
                ),
                "agent_action": "realizability_check(specs=[relaxed_SLOs, CacheHitRateFloor, CacheBurstEviction])",
            },
        },
        "violations": {
            "CacheHitRateFloor": (
                "Redis hot-key eviction caused cache hit rate to drop to 12%, far "
                "below the 50% floor. Without this invariant, the monitoring system "
                "had no trigger to activate defensive measures (rate limiting, cache "
                "scale-out) before the cascade reached the database layer."
            ),
        },
        "trace": {
            1: "Initial: all services running, redis cache_hit_rate=99%, database connections=20% utilized",
            2: "Event: promotional popup \u2192 user-svc query volume 10x \u2192 redis hot-key eviction \u2192 cache_hit_rate drops to 12%",
            3: "Cascade: user-svc cache miss \u2192 all queries hit database \u2192 connection pool=100% \u2192 database timeout",
            4: "Terminal: database unavailable \u2192 order-svc fail \u2192 pay-svc fail \u2192 gateway returns 5xx on all requests",
        },
        "counterexample": {
            1: "state: {redis: cache_hit_rate=99%, database: connections=20%, all services: running} \u2014 healthy",
            2: "action: RedisCacheBurst(user-svc) \u2192 {redis: cache_hit_rate=12%} \u2014 CacheHitRateFloor VIOLATED (if invariant existed)",
            3: "cascade: database connections=100% \u2192 timeout \u2192 {order-svc: down, pay-svc: down} \u2192 full-chain 5xx",
            4: "with CacheHitRateFloor: violation caught at step 2 \u2192 trigger RateLimitService(user-svc) + ScaleUp(redis) \u2192 cascade prevented",
        },
        "tla_spec": (
            "---- MODULE CacheFailureModel ----\n"
            "EXTENDS Naturals\n"
            "CONSTANTS Services, CachedServices, MaxConnections\n"
            "VARIABLES cacheHitRate, dbConnections, serviceStatus, queryVolume\n\n"
            "vars == <<cacheHitRate, dbConnections, serviceStatus, queryVolume>>\n\n"
            "Init ==\n"
            "    /\\ cacheHitRate  = [s \\in CachedServices |-> 99]\n"
            "    /\\ dbConnections = 20\n"
            "    /\\ serviceStatus = [s \\in Services |-> \"running\"]\n"
            "    /\\ queryVolume   = 1\n\n"
            "RedisCacheBurst(s) ==\n"
            "    /\\ s \\in CachedServices\n"
            "    /\\ queryVolume' = queryVolume * 10\n"
            "    /\\ cacheHitRate' = [cacheHitRate EXCEPT ![s] = 12]\n"
            "    /\\ UNCHANGED <<dbConnections, serviceStatus>>\n\n"
            "CacheMissStorm ==\n"
            "    /\\ \\E s \\in CachedServices : cacheHitRate[s] < 50\n"
            "    /\\ dbConnections' = MaxConnections\n"
            "    /\\ UNCHANGED <<cacheHitRate, serviceStatus, queryVolume>>\n\n"
            "DatabaseExhaustion ==\n"
            "    /\\ dbConnections = MaxConnections\n"
            "    /\\ serviceStatus' = [s \\in Services |-> \"down\"]\n"
            "    /\\ UNCHANGED <<cacheHitRate, dbConnections, queryVolume>>\n\n"
            "CacheHitRateFloor ==\n"
            "    \\A s \\in CachedServices : cacheHitRate[s] >= 50\n\n"
            "\\* BMC reverse: terminal state (all down) reached in 3 steps\n"
            "\\* With CacheHitRateFloor, violation caught at step 1\n"
            "====\n"
        ),
    },
}
