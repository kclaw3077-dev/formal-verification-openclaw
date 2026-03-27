"""
Five demo scenarios spanning all four SRE lifecycle phases:
  ① Realizability Check  ② Reactive Synthesis  ③ Runtime BMC  ④ Post-Incident → ①
Text is pulled from locale dicts; structure/data stays here.
"""
from models import (
    AgentOperation, ConstraintDef, InfrastructureState, PropertyViolation,
    Scenario, ScenarioStep, ServiceInfo, ServiceState, TlaSpecRef, TraceStep,
    VerificationReport, VerificationResult,
)
from locales import get_locale

# ---------------------------------------------------------------------------
# Shared initial infrastructure state (大促 pre-scaled topology)
# ---------------------------------------------------------------------------

def _base_state() -> InfrastructureState:
    return InfrastructureState(
        services={
            "gateway": ServiceInfo(
                name="gateway",
                replicas={"east": 3, "west": 3},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=["user-svc", "order-svc", "pay-svc"],
                is_critical=True,
            ),
            "user-svc": ServiceInfo(
                name="user-svc",
                replicas={"east": 3, "west": 3},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=["redis", "database"],
                is_critical=False,
            ),
            "order-svc": ServiceInfo(
                name="order-svc",
                replicas={"east": 3, "west": 3},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=["inventory-svc", "pay-svc"],
                is_critical=True,
            ),
            "pay-svc": ServiceInfo(
                name="pay-svc",
                replicas={"east": 3, "west": 3},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=["database"],
                is_critical=True,
            ),
            "inventory-svc": ServiceInfo(
                name="inventory-svc",
                replicas={"east": 2, "west": 2},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=["database"],
                is_critical=True,
            ),
            "redis": ServiceInfo(
                name="redis",
                replicas={"east": 2, "west": 2},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=[],
                is_critical=False,
                metrics={"cache_hit_rate": 0.99},
            ),
            "database": ServiceInfo(
                name="database",
                replicas={"east": 1, "west": 2},
                state={"east": ServiceState.RUNNING, "west": ServiceState.RUNNING},
                dependencies=[],
                is_critical=True,
            ),
        },
        active_region="east",
        db_write_region="east",
    )


def _clone(state: InfrastructureState) -> InfrastructureState:
    return InfrastructureState.model_validate(state.model_dump())


def _build_constraints(t: dict) -> list[ConstraintDef]:
    return [ConstraintDef(**c) for c in t.get("constraints", [])]


def _build_spec_refs(t: dict) -> list[TlaSpecRef]:
    return [
        TlaSpecRef(filename=fname, defines=ref["defines"], relevant_section=ref["relevant_section"])
        for fname, ref in t.get("spec_refs", {}).items()
    ]


# ---------------------------------------------------------------------------
# Case 1: SLO Conflict Detection (Phase ① Realizability Check)
# ---------------------------------------------------------------------------

def _scenario_1(L: dict) -> Scenario:
    t = L["scenario-1"]
    base = _base_state()
    spec_refs = _build_spec_refs(t)

    # Step 1: Define SLOs → UNREALIZABLE
    # Step 2: Relax specs → REALIZABLE
    return Scenario(
        id="scenario-1",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        phase=t.get("phase", ""),
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                sre_context=t["steps"][1].get("sre_context", ""),
                key_question=t["steps"][1].get("key_question", ""),
                guarantee=t["steps"][1].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="define_slo", params={
                        "availability": "99.99%",
                        "latency_p99": "200ms",
                        "consistency": "strong",
                    }),
                ],
                pre_state=base,
                post_state=base,  # No infra change — spec-level check
                verification=VerificationReport(
                    result=VerificationResult.UNREALIZABLE,
                    operations_checked=[
                        AgentOperation(op_type="define_slo", params={"slos": 3}),
                    ],
                    properties_checked=["Availability_99_99", "LatencyP99_200ms", "StrongConsistency"],
                    violations=[
                        PropertyViolation(
                            property_name="RealizabilityConflict",
                            description=t["violations"]["RealizabilityConflict"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"east": "primary", "west": "replica", "sync_replication": True}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"east": "partitioned", "sync_latency": "280ms"}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"P99": "280ms", "availability": "99.91%"}, violated_property="RealizabilityConflict"),
                            ],
                        ),
                    ],
                    states_explored=256,
                    tla_spec_used="Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"east": "primary", "west": "replica", "sync": True, "healthy": True}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"east": "partitioned", "sync_latency": "280ms"}, violated_property=None),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"P99": "280ms", "availability": "99.91%", "impossible_triangle": True}, violated_property="RealizabilityConflict"),
                    ],
                    conflict_proof=["Availability_99_99", "LatencyP99_200ms", "StrongConsistency"],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                sre_context=t["steps"][2].get("sre_context", ""),
                key_question=t["steps"][2].get("key_question", ""),
                guarantee=t["steps"][2].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="relax_spec", params={
                        "critical_path": "strong+500ms",
                        "query_path": "eventual+200ms",
                    }),
                ],
                pre_state=base,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.REALIZABLE,
                    operations_checked=[
                        AgentOperation(op_type="relax_spec", params={"adjusted": True}),
                    ],
                    properties_checked=["Availability_99_99", "LatencyP99_500ms_critical", "LatencyP99_200ms_query", "EventualConsistency"],
                    violations=[],
                    states_explored=256,
                    tla_spec_used="Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


# ---------------------------------------------------------------------------
# Case 2: Elastic Strategy Synthesis (Phase ② Reactive Synthesis)
# ---------------------------------------------------------------------------

def _scenario_2(L: dict) -> Scenario:
    t = L["scenario-2"]
    base = _base_state()
    spec_refs = _build_spec_refs(t)

    synthesized_controller = {
        "states": ["Normal", "ScalingUp", "RollingUpdate", "Failover"],
        "transitions": [
            {"from": "Normal", "to": "ScalingUp", "guard": "traffic > threshold", "action": "scale_up(bottleneck_first)"},
            {"from": "Normal", "to": "RollingUpdate", "guard": "update_pending ∧ traffic ≤ 8x", "action": "rolling_update(service)"},
            {"from": "Normal", "to": "Failover", "guard": "az_failure_detected", "action": "switch_db_writes → switch_traffic"},
            {"from": "ScalingUp", "to": "Normal", "guard": "all_pods_ready", "action": "complete"},
            {"from": "ScalingUp", "to": "ScalingUp", "guard": "traffic > threshold ∧ ¬rolling_update", "action": "scale_up(next)"},
            {"from": "RollingUpdate", "to": "Normal", "guard": "update_complete", "action": "complete"},
        ],
        "guards": [
            "traffic_multiplier ≤ 8 ∨ ¬rolling_update_in_progress",
            "inventory-svc scaled before order-svc",
            "switch_db_writes before switch_traffic on failover",
            "EffectiveCapacity ≥ AvailabilityFloor at all times",
        ],
        "total_states": 4,
        "total_transitions": 12,
        "total_guards": 6,
    }

    return Scenario(
        id="scenario-2",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        phase=t.get("phase", ""),
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                sre_context=t["steps"][1].get("sre_context", ""),
                key_question=t["steps"][1].get("key_question", ""),
                guarantee=t["steps"][1].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="synthesize", params={
                        "env_model": {"traffic": "1x-10x", "max_pods": 20},
                        "safety_specs": ["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                    }),
                ],
                pre_state=base,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="synthesize", params={"phase": "input"}),
                    ],
                    properties_checked=["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                    violations=[],
                    states_explored=4096,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["trace"][1], state_snapshot={"traffic_levels": "1x,2x,4x,8x,10x"}, violated_property=None),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                sre_context=t["steps"][2].get("sre_context", ""),
                key_question=t["steps"][2].get("key_question", ""),
                guarantee=t["steps"][2].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="synthesis_guard", params={
                        "guard": "traffic > 8x → mutex(scale, rolling_update)",
                    }),
                ],
                pre_state=base,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="synthesis_guard", params={"discovered": True}),
                    ],
                    properties_checked=["AvailabilityFloor"],
                    violations=[],
                    states_explored=4096,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["trace"][1], state_snapshot={"traffic_levels": "1x,2x,4x,8x,10x"}, violated_property=None),
                        TraceStep(step=2, description=t["trace"][2], state_snapshot={"traffic": "8x", "capacity_during_update": "66%"}, violated_property=None),
                        TraceStep(step=3, description=t["trace"][3], state_snapshot={"traffic": "8x", "concurrent_scale": True, "capacity": "<66%"}, violated_property=None),
                        TraceStep(step=4, description=t["trace"][4], state_snapshot={"guard_added": "traffic≤8x ∨ ¬rolling_update"}, violated_property=None),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=3,
                title=t["steps"][3]["title"],
                description=t["steps"][3]["description"],
                agent_action=t["steps"][3]["agent_action"],
                sre_context=t["steps"][3].get("sre_context", ""),
                key_question=t["steps"][3].get("key_question", ""),
                guarantee=t["steps"][3].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="synthesis_output", params={
                        "states": 4, "transitions": 12, "guards": 6,
                    }),
                ],
                pre_state=base,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="synthesis_output", params={"complete": True}),
                    ],
                    properties_checked=["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                    violations=[],
                    states_explored=4096,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    synthesized_controller=synthesized_controller,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


# ---------------------------------------------------------------------------
# Case 3: Change Verification — Emergency Hotfix (Phase ③ BMC-Change)
# ---------------------------------------------------------------------------

def _scenario_3(L: dict) -> Scenario:
    t = L["scenario-3"]
    base = _base_state()
    # Pre-scaled for 大促: inventory-svc at 4 replicas
    base.services["inventory-svc"].replicas = {"east": 2, "west": 2}
    spec_refs = _build_spec_refs(t)

    # Step 1: rolling update → UNSAFE (compound failure)
    s1_post = _clone(base)
    s1_post.services["inventory-svc"].state["east"] = ServiceState.DEPLOYING
    s1_post.services["order-svc"].state["east"] = ServiceState.DEGRADED  # GC pause

    # Step 2: scale to 6 first → SAFE
    s2_base = _clone(base)
    s2_base.services["inventory-svc"].replicas = {"east": 3, "west": 3}
    s2_post = _clone(s2_base)
    s2_post.services["inventory-svc"].state["east"] = ServiceState.DEPLOYING

    return Scenario(
        id="scenario-3",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        phase=t.get("phase", ""),
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                sre_context=t["steps"][1].get("sre_context", ""),
                key_question=t["steps"][1].get("key_question", ""),
                guarantee=t["steps"][1].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="rolling_update", params={"service": "inventory-svc", "strategy": "one-at-a-time"}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="rolling_update", params={"service": "inventory-svc"}),
                    ],
                    properties_checked=["AvailabilityFloor", "MinimumRedundancy"],
                    violations=[
                        PropertyViolation(
                            property_name="AvailabilityFloor",
                            description=t["violations"]["AvailabilityFloor"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"inventory-svc": "2E/2W running", "throughput": "100%"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"inventory-svc.east": "1 running + 1 deploying", "throughput": "75%"}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"order-svc.east": "2 running + 1 degraded", "throughput": "50%"}, violated_property="AvailabilityFloor"),
                            ],
                        ),
                    ],
                    states_explored=1847,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"inventory-svc": "2E/2W", "order-svc": "3E/3W"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"inventory-svc.east": "1+1 deploying", "throughput": "75%"}, violated_property=None),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"order-svc.east": "2+1 degraded", "throughput": "50%"}, violated_property="AvailabilityFloor"),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                sre_context=t["steps"][2].get("sre_context", ""),
                key_question=t["steps"][2].get("key_question", ""),
                guarantee=t["steps"][2].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="scale_up", params={"service": "inventory-svc", "to": 6}),
                    AgentOperation(op_type="rolling_update", params={"service": "inventory-svc"}),
                ],
                pre_state=s2_base,
                post_state=s2_post,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="scale_up", params={"service": "inventory-svc", "to": 6}),
                        AgentOperation(op_type="rolling_update", params={"service": "inventory-svc"}),
                    ],
                    properties_checked=["AvailabilityFloor", "MinimumRedundancy"],
                    violations=[],
                    states_explored=1847,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


# ---------------------------------------------------------------------------
# Case 4: Fault Interception — Failover Split-Brain (Phase ③ BMC-Fault)
# ---------------------------------------------------------------------------

def _scenario_4(L: dict) -> Scenario:
    t = L["scenario-4"]
    base = _base_state()
    # Database east is having issues
    base.services["database"].state["east"] = ServiceState.DEGRADED
    spec_refs = _build_spec_refs(t)

    # Step 1: SwitchTraffic first → UNSAFE (split-brain)
    s1_post = _clone(base)
    s1_post.active_region = "west"
    # dbWriteRegion still east → mismatch!

    # Step 2: SwitchDBWrites first → SAFE
    s2_post = _clone(base)
    s2_post.db_write_region = "west"
    s2_post.active_region = "west"

    return Scenario(
        id="scenario-4",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        phase=t.get("phase", ""),
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                sre_context=t["steps"][1].get("sre_context", ""),
                key_question=t["steps"][1].get("key_question", ""),
                guarantee=t["steps"][1].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                    AgentOperation(op_type="switch_db_writes", params={"target_region": "west"}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                    ],
                    properties_checked=["TrafficWriteConsistency", "NoSplitBrain"],
                    violations=[
                        PropertyViolation(
                            property_name="TrafficWriteConsistency",
                            description=t["violations"]["TrafficWriteConsistency"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"activeRegion": "east", "dbWriteRegion": "east"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east"}, violated_property="TrafficWriteConsistency"),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east", "split_brain_risk": True}, violated_property="TrafficWriteConsistency"),
                            ],
                        ),
                    ],
                    states_explored=3841,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"activeRegion": "east", "dbWriteRegion": "east", "consistent": True}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east", "consistent": False}, violated_property="TrafficWriteConsistency"),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"split_brain": True, "data_inconsistency": True}, violated_property="TrafficWriteConsistency"),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                sre_context=t["steps"][2].get("sre_context", ""),
                key_question=t["steps"][2].get("key_question", ""),
                guarantee=t["steps"][2].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="switch_db_writes", params={"target_region": "west"}),
                    AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                ],
                pre_state=base,
                post_state=s2_post,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="switch_db_writes", params={"target_region": "west"}),
                        AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                    ],
                    properties_checked=["TrafficWriteConsistency", "NoSplitBrain"],
                    violations=[],
                    states_explored=3841,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


# ---------------------------------------------------------------------------
# Case 5: Fault Retrospective & Feedback Loop (Phase ④ → ①)
# ---------------------------------------------------------------------------

def _scenario_5(L: dict) -> Scenario:
    t = L["scenario-5"]
    base = _base_state()
    spec_refs = _build_spec_refs(t)

    # Step 1: BMC reverse — trace fault path
    s1_post = _clone(base)
    s1_post.services["redis"].metrics = {"cache_hit_rate": 0.12}
    s1_post.services["user-svc"].state["east"] = ServiceState.DEGRADED
    s1_post.services["database"].state["east"] = ServiceState.DOWN
    s1_post.services["order-svc"].state["east"] = ServiceState.DOWN
    s1_post.services["pay-svc"].state["east"] = ServiceState.DOWN

    # Step 2: Generate new invariant — CacheHitRateFloor catches it
    s2_post = _clone(base)
    s2_post.services["redis"].metrics = {"cache_hit_rate": 0.12}
    # With CacheHitRateFloor, this would be caught immediately

    # Step 3: Feed back to Phase 1 — REALIZABLE
    # State stays as base (specs are realizable)

    return Scenario(
        id="scenario-5",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        phase=t.get("phase", ""),
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                sre_context=t["steps"][1].get("sre_context", ""),
                key_question=t["steps"][1].get("key_question", ""),
                guarantee=t["steps"][1].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="bmc_reverse", params={"terminal_state": "full_chain_5xx", "max_depth": 5}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="bmc_reverse", params={"terminal_state": "full_chain_5xx"}),
                    ],
                    properties_checked=["CacheHitRateFloor", "AvailabilityFloor", "MinimumRedundancy"],
                    violations=[
                        PropertyViolation(
                            property_name="CacheHitRateFloor",
                            description=t["violations"]["CacheHitRateFloor"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"redis.cache_hit_rate": "99%", "database.connections": "20%"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"redis.cache_hit_rate": "12%", "user-svc": "cache_miss_storm"}, violated_property="CacheHitRateFloor"),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"database.connections": "100%", "database": "timeout"}, violated_property=None),
                                TraceStep(step=4, description=t["trace"][4], state_snapshot={"order-svc": "down", "pay-svc": "down", "gateway": "5xx"}, violated_property="AvailabilityFloor"),
                            ],
                        ),
                    ],
                    states_explored=2048,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"redis.cache_hit_rate": "99%", "all_services": "running"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"redis.cache_hit_rate": "12%"}, violated_property="CacheHitRateFloor"),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"database": "down", "order-svc": "down", "pay-svc": "down"}, violated_property="AvailabilityFloor"),
                        TraceStep(step=4, description=t["counterexample"][4], state_snapshot={"with_invariant": "caught_at_step_2", "cascade": "prevented"}, violated_property=None),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                sre_context=t["steps"][2].get("sre_context", ""),
                key_question=t["steps"][2].get("key_question", ""),
                guarantee=t["steps"][2].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="propose_invariant", params={"name": "CacheHitRateFloor", "threshold": "50%"}),
                ],
                pre_state=s2_post,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="propose_invariant", params={"name": "CacheHitRateFloor"}),
                    ],
                    properties_checked=["CacheHitRateFloor"],
                    violations=[],
                    states_explored=2048,
                    tla_spec_used="Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
            ScenarioStep(
                step_id=3,
                title=t["steps"][3]["title"],
                description=t["steps"][3]["description"],
                agent_action=t["steps"][3]["agent_action"],
                sre_context=t["steps"][3].get("sre_context", ""),
                key_question=t["steps"][3].get("key_question", ""),
                guarantee=t["steps"][3].get("guarantee", ""),
                operations=[
                    AgentOperation(op_type="realizability_check", params={
                        "specs": ["relaxed_SLOs", "CacheHitRateFloor", "CacheBurstEviction"],
                    }),
                ],
                pre_state=base,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.REALIZABLE,
                    operations_checked=[
                        AgentOperation(op_type="realizability_check", params={"expanded_specs": True}),
                    ],
                    properties_checked=["Availability_99_99", "LatencyP99_500ms", "EventualConsistency", "CacheHitRateFloor"],
                    violations=[],
                    states_explored=512,
                    tla_spec_used="Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_BUILDERS = {
    "scenario-1": _scenario_1,
    "scenario-2": _scenario_2,
    "scenario-3": _scenario_3,
    "scenario-4": _scenario_4,
    "scenario-5": _scenario_5,
}


def get_scenario(scenario_id: str, lang: str = "en") -> Scenario:
    builder = _BUILDERS.get(scenario_id)
    if builder is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return builder(get_locale(lang))


def list_scenarios(lang: str = "en") -> list[dict]:
    L = get_locale(lang)
    return [
        {"id": sid, "title": L[sid]["title"], "subtitle": L[sid]["subtitle"], "phase": L[sid].get("phase", "")}
        for sid in _BUILDERS
    ]
