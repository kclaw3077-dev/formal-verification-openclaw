"""English locale — all user-facing scenario text."""

SCENARIOS = {
    # ── Scenario 1 ──────────────────────────────────────────────────────────
    "scenario-1": {
        "title": "Scenario 1: Rolling Update Capacity Bottleneck",
        "subtitle": "A safe-looking update triggers a hidden throughput crisis",
        "description": (
            "Agent receives instruction: rolling-update order-svc from v1 to v2. "
            "The update takes 1 replica offline at a time (2/3 remain). Seems safe. "
            "But inventory-svc (which order-svc depends on) has only 2 east replicas, "
            "and one is in GC pause. TLA+ model checking explores the full request chain "
            "and discovers that effective throughput drops below the safety threshold."
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) >= 66%",
                "threshold": "66%",
                "description": "Effective capacity on any critical request path must stay above 66%",
            },
            {
                "name": "MinSafeReplicas",
                "expression": "TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "order-svc: 2, inventory-svc: 2",
                "description": "Rolling update keeps at least 2/3 replicas running at all times",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "serviceState", "RollingUpdate", "ReplicaFailure", "EffectiveCapacity"],
                "relevant_section": "Models service state transitions and rolling update reducing effective capacity while a dependency is degraded",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                "relevant_section": "AvailabilityFloor invariant catches the chain throughput drop below the 66% safety floor",
            },
        },
        "steps": {
            1: {
                "title": "Background: inventory-svc GC Pause",
                "description": (
                    "inventory-svc east replica #2 enters a long GC pause. "
                    "Effective east capacity drops to 1/2. "
                    "Since this is an environment event (not an Agent action), "
                    "the verification gate only performs basic health monitoring: "
                    "replica count is still 2 (the pod is running, just slow), "
                    "so MinimumRedundancy passes. "
                    "AvailabilityFloor (chain throughput analysis) is only triggered "
                    "when the Agent proposes a change."
                ),
                "agent_action": "[Environment Event] inventory-svc GC pause detected",
            },
            2: {
                "title": "Agent Action: Rolling Update order-svc",
                "description": (
                    "Agent proposes: rolling-update order-svc east (v1\u2192v2). "
                    "During the update, 1 of 3 order-svc replicas is being replaced, "
                    "so order-svc effective capacity = 2.5/3. "
                    "But order-svc depends on inventory-svc, which is already at 1/2 capacity. "
                    "The combined chain capacity: min(2.5/3, 1/2) = 50% \u2014 BELOW the safety floor."
                ),
                "agent_action": "rolling_update(order-svc, east, v1\u2192v2)",
            },
        },
        "violations": {
            "AvailabilityFloor": (
                "Effective capacity on critical path drops below safety threshold. "
                "order-svc (deploying) \u2192 inventory-svc (degraded): "
                "chain throughput = min(83%, 50%) = 50%, below the 66% floor."
            ),
        },
        "trace": {
            1: "Initial state: all services running",
            2: "inventory-svc east replica enters GC pause",
            3: "Agent starts rolling update on order-svc east",
        },
        "counterexample": {
            1: "Init: all healthy",
            2: "ReplicaFailure(inventory-svc, east)",
            3: "RollingUpdate(order-svc, east)",
        },
        "tla_spec": (
            "\\* Key invariant violated:\n"
            "AvailabilityFloor ==\n"
            "    \\A s \\in CriticalPath :\n"
            "        EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]\n\n"
            "\\* The model checker explores the state where:\n"
            "\\* - inventory-svc is degraded (GC pause)\n"
            "\\* - order-svc enters deploying state\n"
            "\\* Combined chain capacity falls below threshold."
        ),
    },

    # ── Scenario 2 ──────────────────────────────────────────────────────────
    "scenario-2": {
        "title": "Scenario 2: Hidden Circular Dependency",
        "subtitle": "A refund feature creates an invisible deadlock risk",
        "description": (
            "Agent receives instruction: add order-status-check to pay-svc's refund flow "
            "(pay-svc now calls order-svc). Current dependency: order-svc \u2192 pay-svc (for payment). "
            "This creates order-svc \u21c4 pay-svc bidirectional dependency. "
            "The cycle only triggers on the refund path, invisible in normal payment flow. "
            "TLA+ transitive closure analysis catches the cycle instantly."
        ),
        "constraints": [
            {
                "name": "NoCyclicDependencies",
                "expression": "\\A s \\in Services : s \\notin ReachableFrom(s, {}, deps)",
                "threshold": "0 cycles",
                "description": "The service dependency graph must be a DAG \u2014 no circular dependencies allowed",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "dependencies", "AddDependency", "ReachableFrom"],
                "relevant_section": "Models the dependency graph and transitive closure computation for cycle detection",
            },
            "Properties.tla": {
                "defines": ["NoCyclicDependencies", "HasCycle"],
                "relevant_section": "NoCyclicDependencies invariant uses transitive closure to detect any cycle in the dependency graph",
            },
        },
        "steps": {
            1: {
                "title": "Agent Action: Add Refund Verification Dependency",
                "description": (
                    "The product team requests: before processing refunds, pay-svc should "
                    "verify the order status by calling order-svc. This seems like a reasonable "
                    "business requirement. Agent proposes adding this dependency."
                ),
                "agent_action": "add_dependency(pay-svc \u2192 order-svc, purpose='refund_verification')",
            },
            2: {
                "title": "TLA+ Suggests: Break the Cycle",
                "description": (
                    "The verifier not only catches the cycle but the model shows that "
                    "an alternative design \u2014 using an async event bus instead of synchronous call \u2014 "
                    "would eliminate the circular dependency. pay-svc publishes a 'refund_requested' event, "
                    "and a separate reconciliation service checks order status."
                ),
                "agent_action": "[Recommendation] Use event-driven pattern to avoid sync cycle",
            },
        },
        "violations": {
            "NoCyclicDependencies": (
                "Circular dependency detected: "
                "order-svc \u2192 pay-svc \u2192 order-svc. "
                "This cycle creates a deadlock risk: if order-svc is slow, "
                "pay-svc refund calls block, which blocks order-svc's payment callbacks, "
                "creating a cascading timeout spiral."
            ),
        },
        "trace": {
            1: "Current: order-svc depends on pay-svc",
            2: "Proposed: pay-svc adds dependency on order-svc",
            3: "Cycle found: order-svc \u2192 pay-svc \u2192 order-svc",
        },
        "counterexample": {
            1: "Init: DAG is acyclic",
            2: "AddDependency(pay-svc, order-svc)",
        },
        "tla_spec": (
            "\\* Cycle detection via transitive closure:\n"
            "RECURSIVE ReachableFrom(_,_,_)\n"
            "ReachableFrom(s, visited, deps) ==\n"
            "    LET directDeps == deps[s] \\\\ visited\n"
            "    IN  directDeps \\cup\n"
            "        UNION {ReachableFrom(d, visited \\cup directDeps, deps) : d \\in directDeps}\n\n"
            "HasCycle(deps) ==\n"
            "    \\E s \\in Services : s \\in ReachableFrom(s, {}, deps)\n\n"
            "NoCyclicDependencies == ~HasCycle(dependencies)"
        ),
    },

    # ── Scenario 3 ──────────────────────────────────────────────────────────
    "scenario-3": {
        "title": "Scenario 3: Split-Brain During Failover",
        "subtitle": "A 3-step failover plan has a race condition window",
        "description": (
            "Agent receives instruction: failover from Region-East to Region-West. "
            "Agent's plan: (1) switch DNS to west, (2) wait 30s for connections to drain, "
            "(3) switch DB writes to west. TLA+ discovers that between step 1 and step 3, "
            "traffic goes to west but DB writes still go to east \u2014 reads from west see stale data. "
            "Worse: if step 3 fails (network partition), the system is permanently inconsistent."
        ),
        "constraints": [
            {
                "name": "TrafficWriteConsistency",
                "expression": "activeRegion = dbWriteRegion",
                "threshold": "always equal",
                "description": "The traffic-serving region and DB write region must always be the same to avoid stale reads",
            },
            {
                "name": "NoSplitBrain",
                "expression": "dbWriteRegion \\in Regions",
                "threshold": "exactly 1 region",
                "description": "At most one region may accept DB writes at any time \u2014 never both simultaneously",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Regions", "activeRegion", "dbWriteRegion", "SwitchTraffic", "SwitchDBWrites"],
                "relevant_section": "Models the multi-region failover state machine with separate traffic and write switches",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "NoSplitBrain"],
                "relevant_section": "TrafficWriteConsistency catches the window where traffic and writes are in different regions",
            },
        },
        "steps": {
            1: {
                "title": "Agent Action: Switch Traffic to West",
                "description": (
                    "Agent executes step 1 of failover: update DNS to point to Region-West. "
                    "New requests now go to west. But DB writes are still going to east. "
                    "Any writes from west-region services go to east DB (cross-region latency), "
                    "and reads from west replicas may see stale data."
                ),
                "agent_action": "switch_traffic(west)",
            },
            2: {
                "title": "TLA+ Suggests: Atomic Failover Protocol",
                "description": (
                    "The correct order is: (1) stop east writes, (2) wait for replication sync, "
                    "(3) enable west writes, (4) switch traffic. This ensures consistency at every step. "
                    "TLA+ verifies this alternative sequence satisfies TrafficWriteConsistency "
                    "at every intermediate state."
                ),
                "agent_action": "[Corrected Plan] stop_writes(east) \u2192 sync \u2192 enable_writes(west) \u2192 switch_traffic(west)",
            },
        },
        "violations": {
            "TrafficWriteConsistency": (
                "After switching traffic to west, DB writes remain in east. "
                "State: activeRegion=west, dbWriteRegion=east. "
                "This violates TrafficWriteConsistency: reads may return stale data. "
                "Duration of inconsistency depends on when step 3 completes."
            ),
        },
        "trace": {
            1: "Init: traffic=east, writes=east (consistent)",
            2: "SwitchTraffic(west): traffic=west, writes=east",
        },
        "counterexample": {
            1: "Init: activeRegion=east, dbWriteRegion=east",
            2: "SwitchTraffic(west)",
            3: "[Network Partition] SwitchDBWrites fails",
        },
        "tla_spec": (
            "\\* The two key properties:\n"
            "NoSplitBrain ==\n"
            "    dbWriteRegion \\in Regions  \\* never \"both\"\n\n"
            "TrafficWriteConsistency ==\n"
            "    activeRegion = dbWriteRegion\n\n"
            "\\* TLC finds that SwitchTraffic(west) before SwitchDBWrites(west)\n"
            "\\* creates an intermediate state violating TrafficWriteConsistency.\n"
            "\\* The safe sequence: switch writes first, then traffic."
        ),
    },

    # ── Scenario 4 ──────────────────────────────────────────────────────────
    "scenario-4": {
        "title": "Scenario 4: Concurrent Operations Conflict",
        "subtitle": "Two safe operations combine into a dangerous state",
        "description": (
            "Agent receives two independent maintenance requests: "
            "(A) security-patch user-svc, (B) expand database replicas. "
            "Each operation is individually safe. But TLA+ state space exploration "
            "discovers that when both execute concurrently, user-svc restarts and "
            "reconnects to a database that's mid-rebalance. Connection storms + "
            "rebalance overhead cascade into a cluster-wide outage."
        ),
        "constraints": [
            {
                "name": "NoSimultaneousUpdatesOnChain",
                "expression": "\\A s, t on same chain : ~(deploying(s) /\\ deploying(t))",
                "threshold": "max 1 deploying per chain",
                "description": "No two services on the same dependency chain may be in deploying state simultaneously",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "dependencies", "serviceState", "RollingUpdate", "ScaleUp"],
                "relevant_section": "Models concurrent execution of rolling update and scale-up as interleaved state transitions",
            },
            "Properties.tla": {
                "defines": ["NoSimultaneousUpdatesOnChain", "AvailabilityFloor"],
                "relevant_section": "NoSimultaneousUpdatesOnChain detects the dangerous interleaving where user-svc and database deploy concurrently",
            },
        },
        "steps": {
            1: {
                "title": "Request A: Security Patch user-svc",
                "description": (
                    "Security team requests: apply CVE-2024-XXXX patch to user-svc. "
                    "Requires rolling restart. Individually safe: 3 replicas, "
                    "rolling update keeps 2 running at all times."
                ),
                "agent_action": "rolling_update(user-svc, east, security_patch)",
            },
            2: {
                "title": "Request B: Database Replica Expansion",
                "description": (
                    "DBA team requests: add 1 replica to database east for capacity. "
                    "Individually safe: adding replicas doesn't disrupt existing ones. "
                    "But during rebalance, existing replicas have higher latency."
                ),
                "agent_action": "scale_up(database, east, 1) + rebalance",
            },
            3: {
                "title": "Combined: Both Operations Concurrent",
                "description": (
                    "When both operations execute simultaneously, TLA+ finds a dangerous interleaving: "
                    "(1) user-svc replica restarts, (2) reconnects to database, "
                    "(3) database is mid-rebalance \u2192 connection refused, "
                    "(4) user-svc retry storm overwhelms database, "
                    "(5) other services' DB connections also get rejected. "
                    "This is a combinatorial explosion that humans easily miss."
                ),
                "agent_action": "[CONCURRENT] rolling_update(user-svc) + scale_up(database)",
            },
        },
        "violations": {
            "NoSimultaneousUpdatesOnChain": (
                "user-svc and database are on the same dependency chain "
                "(user-svc \u2192 database). Both entering deploying state simultaneously "
                "violates the NoSimultaneousUpdatesOnChain property. "
                "During the overlap window, user-svc reconnection storm + "
                "database rebalance creates cascading failures."
            ),
        },
        "trace": {
            1: "Init: all services running",
            2: "RollingUpdate(user-svc, east)",
            3: "ScaleUp(database, east, 1) triggers rebalance",
        },
        "counterexample": {
            1: "Init: all running",
            2: "RollingUpdate(user-svc, east)",
            3: "ScaleUp(database, east, 1) + rebalance",
        },
        "tla_spec": (
            "\\* Key property: no two services on the same chain update simultaneously\n"
            "NoSimultaneousUpdatesOnChain ==\n"
            "    \\A s \\in Services : \\A t \\in dependencies[s] :\n"
            "        ~(\\E r1, r2 \\in Regions :\n"
            "            serviceState[s][r1] = \"deploying\" /\\ serviceState[t][r2] = \"deploying\")\n\n"
            "\\* TLC explores 8,923 states and finds the interleaving where\n"
            "\\* user-svc and database are both deploying on the same chain.\n"
            "\\* Each operation alone is safe; the combination is not."
        ),
    },

    # ── Scenario 5 ──────────────────────────────────────────────────────────
    "scenario-5": {
        "title": "Scenario 5: Scale-Down Cascade Effect",
        "subtitle": "Cost optimization creates a single point of failure",
        "description": (
            "Agent observes low traffic at 3 AM and proposes: scale inventory-svc east "
            "from 2 to 1 replica to save costs. Looks reasonable \u2014 traffic is 20% of peak. "
            "But TLA+ exhaustively checks all post-scale-down states including failure scenarios: "
            "if the single remaining replica fails, order-svc and pay-svc both lose inventory "
            "capability. System availability drops from 99.9% to 0% on the critical path. "
            "Recovery time (new replica + data warmup) exceeds SLA maximum downtime."
        ),
        "constraints": [
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "inventory-svc: \u2265 2",
                "description": "Critical-path services must maintain minimum replicas even in failure scenarios after the change",
            },
            {
                "name": "SLA Compliance",
                "expression": "RecoveryTime(s) <= MaxDowntime",
                "threshold": "recovery < 5 min",
                "description": "Recovery time from any single failure must stay within SLA maximum downtime window",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "CriticalPath", "TotalReplicas", "ScaleDown", "ReplicaFailure"],
                "relevant_section": "Models scale-down followed by replica failure, exploring all post-change reachable states",
            },
            "Properties.tla": {
                "defines": ["MinimumRedundancy", "AvailabilityFloor", "NoCyclicDependencies"],
                "relevant_section": "MinimumRedundancy invariant proves the operation is unsafe by finding a reachable state where TotalReplicas = 0",
            },
        },
        "steps": {
            1: {
                "title": "Agent Proposal: Cost-Optimized Scale Down",
                "description": (
                    "It's 3 AM, traffic is at 20% of peak. Agent's cost optimization module "
                    "suggests: scale inventory-svc east from 2\u21921 replica, saving $47/month. "
                    "Current load can be served by 1 replica with 60% headroom."
                ),
                "agent_action": "scale_down(inventory-svc, east, 1)  # save costs at low traffic",
            },
            2: {
                "title": "Formal Guarantee: No-Degradation Principle",
                "description": (
                    "The No-Degradation Principle formalized in TLA+: "
                    "for ALL reachable states after the operation (including failure states), "
                    "availability must not decrease. This is stronger than just checking "
                    "the immediate post-operation state \u2014 it checks every possible future. "
                    "The $47/month savings is not worth the risk of violating SLA."
                ),
                "agent_action": "[BLOCKED] Operation rejected by verification gate",
            },
        },
        "violations": {
            "MinimumRedundancy": (
                "After scaling to 1 replica, inventory-svc east has no redundancy. "
                "TLA+ explores the successor state where this single replica fails: "
                "TotalReplicas(inventory-svc) in east = 0, which is below "
                "MinSafeReplicas[inventory-svc] = 2. "
                "This creates a single point of failure on the critical path "
                "(gateway \u2192 order-svc \u2192 inventory-svc)."
            ),
        },
        "trace": {
            1: "Init: inventory-svc east = 2 replicas",
            2: "ScaleDown(inventory-svc, east, 1)",
            3: "ReplicaFailure(inventory-svc, east) \u2014 single point fails",
            4: "Cascade: order-svc cannot reach inventory-svc",
        },
        "counterexample": {
            1: "Init: inventory-svc.east=running(2)",
            2: "ScaleDown(inventory-svc, east, 1)",
            3: "ReplicaFailure(inventory-svc, east)",
        },
        "tla_spec": (
            "\\* No-Degradation: minimum redundancy must hold in ALL reachable states\n"
            "\\* including failure scenarios after the proposed change.\n"
            "MinimumRedundancy ==\n"
            "    \\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]\n\n"
            "\\* TLC checks this invariant across ALL reachable states.\n"
            "\\* After ScaleDown(inventory-svc, east, 1), TLC explores:\n"
            "\\*   ScaleDown \u2192 ReplicaFailure \u2192 TotalReplicas = 0 < 2 = MinSafe\n"
            "\\* The invariant violation proves the operation is unsafe\n"
            "\\* even though the IMMEDIATE post-state looks fine."
        ),
    },
}
