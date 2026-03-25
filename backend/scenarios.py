"""
Five demo scenarios showcasing formal verification for SRE Agent operations.
Text is pulled from locale dicts; structure/data stays here.
"""
from models import (
    AgentOperation, ConstraintDef, InfrastructureState, PropertyViolation,
    Scenario, ScenarioStep, ServiceInfo, ServiceState, TlaSpecRef, TraceStep,
    VerificationReport, VerificationResult,
)
from locales import get_locale

# ---------------------------------------------------------------------------
# Shared initial infrastructure state
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
                dependencies=["database"],
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
# Scenario builders — each reads text from locale `L`
# ---------------------------------------------------------------------------

def _scenario_1(L: dict) -> Scenario:
    t = L["scenario-1"]
    base = _base_state()

    s1_state = _clone(base)
    s1_state.services["inventory-svc"].replicas["east"] = 1
    s1_state.services["inventory-svc"].state["east"] = ServiceState.DEGRADED

    s2_pre = _clone(s1_state)
    s2_post = _clone(s1_state)
    s2_post.services["order-svc"].state["east"] = ServiceState.DEPLOYING

    spec_refs = _build_spec_refs(t)

    return Scenario(
        id="scenario-1",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                operations=[],
                pre_state=base,
                post_state=s1_state,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[],
                    properties_checked=["MinimumRedundancy"],
                    violations=[],
                    states_explored=48,
                    tla_spec_used="SREInfrastructure.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                operations=[
                    AgentOperation(op_type="rolling_update", params={"service": "order-svc", "region": "east", "from_version": "v1", "to_version": "v2"}),
                ],
                pre_state=s2_pre,
                post_state=s2_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="rolling_update", params={"service": "order-svc", "region": "east"}),
                    ],
                    properties_checked=["MinimumRedundancy", "AvailabilityFloor", "NoSimultaneousUpdatesOnChain"],
                    violations=[
                        PropertyViolation(
                            property_name="AvailabilityFloor",
                            description=t["violations"]["AvailabilityFloor"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"order-svc": "3/3", "inventory-svc": "2/2"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"order-svc": "3/3", "inventory-svc": "1/2 (degraded)"}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"order-svc": "2.5/3 (deploying)", "inventory-svc": "1/2 (degraded)"}, violated_property="AvailabilityFloor"),
                            ],
                        ),
                    ],
                    states_explored=1247,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"order-svc.east": "running(3)", "inventory-svc.east": "running(2)"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"order-svc.east": "running(3)", "inventory-svc.east": "degraded(1)"}, violated_property=None),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"order-svc.east": "deploying(3)", "inventory-svc.east": "degraded(1)"}, violated_property="AvailabilityFloor"),
                    ],
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


def _scenario_2(L: dict) -> Scenario:
    t = L["scenario-2"]
    base = _base_state()

    s1_post = _clone(base)
    s1_post.services["pay-svc"].dependencies.append("order-svc")

    spec_refs = _build_spec_refs(t)

    return Scenario(
        id="scenario-2",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                operations=[
                    AgentOperation(op_type="add_dep", params={"from": "pay-svc", "to": "order-svc", "purpose": "refund_verification"}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="add_dep", params={"from": "pay-svc", "to": "order-svc"}),
                    ],
                    properties_checked=["NoCyclicDependencies", "MinimumRedundancy", "AvailabilityFloor"],
                    violations=[
                        PropertyViolation(
                            property_name="NoCyclicDependencies",
                            description=t["violations"]["NoCyclicDependencies"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"order-svc.deps": ["inventory-svc", "pay-svc"]}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"pay-svc.deps": ["database", "order-svc"]}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"cycle": ["order-svc", "pay-svc", "order-svc"]}, violated_property="NoCyclicDependencies"),
                            ],
                        ),
                    ],
                    states_explored=892,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"dependencies": "order-svc\u2192{inventory-svc,pay-svc}, pay-svc\u2192{database}"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"dependencies": "order-svc\u2192{inventory-svc,pay-svc}, pay-svc\u2192{database,order-svc}"}, violated_property="NoCyclicDependencies"),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                operations=[],
                pre_state=s1_post,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[],
                    properties_checked=["NoCyclicDependencies"],
                    violations=[],
                    states_explored=892,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


def _scenario_3(L: dict) -> Scenario:
    t = L["scenario-3"]
    base = _base_state()

    s1_post = _clone(base)
    s1_post.active_region = "west"

    s3_post = _clone(s1_post)
    s3_post.db_write_region = "west"

    spec_refs = _build_spec_refs(t)

    return Scenario(
        id="scenario-3",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                operations=[
                    AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                    ],
                    properties_checked=["NoSplitBrain", "TrafficWriteConsistency"],
                    violations=[
                        PropertyViolation(
                            property_name="TrafficWriteConsistency",
                            description=t["violations"]["TrafficWriteConsistency"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"activeRegion": "east", "dbWriteRegion": "east"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east"}, violated_property="TrafficWriteConsistency"),
                            ],
                        ),
                    ],
                    states_explored=3841,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"activeRegion": "east", "dbWriteRegion": "east", "consistent": True}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east", "consistent": False}, violated_property="TrafficWriteConsistency"),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"activeRegion": "west", "dbWriteRegion": "east", "consistent": False, "partition": True}, violated_property="TrafficWriteConsistency"),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                operations=[
                    AgentOperation(op_type="switch_db_writes", params={"target_region": "west"}),
                    AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                ],
                pre_state=base,
                post_state=s3_post,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="switch_db_writes", params={"target_region": "west"}),
                        AgentOperation(op_type="switch_traffic", params={"target_region": "west"}),
                    ],
                    properties_checked=["NoSplitBrain", "TrafficWriteConsistency"],
                    violations=[],
                    states_explored=3841,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


def _scenario_4(L: dict) -> Scenario:
    t = L["scenario-4"]
    base = _base_state()

    s1_post = _clone(base)
    s1_post.services["user-svc"].state["east"] = ServiceState.DEPLOYING
    s1_post.services["database"].state["east"] = ServiceState.DEPLOYING

    spec_refs = _build_spec_refs(t)

    return Scenario(
        id="scenario-4",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                operations=[
                    AgentOperation(op_type="rolling_update", params={"service": "user-svc", "region": "east", "reason": "security_patch"}),
                ],
                pre_state=base,
                post_state=_clone(base),
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="rolling_update", params={"service": "user-svc", "region": "east"}),
                    ],
                    properties_checked=["MinimumRedundancy", "AvailabilityFloor", "NoSimultaneousUpdatesOnChain"],
                    violations=[],
                    states_explored=634,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                operations=[
                    AgentOperation(op_type="scale_up", params={"service": "database", "region": "east", "amount": 1}),
                ],
                pre_state=base,
                post_state=_clone(base),
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[
                        AgentOperation(op_type="scale_up", params={"service": "database", "region": "east", "amount": 1}),
                    ],
                    properties_checked=["MinimumRedundancy", "AvailabilityFloor"],
                    violations=[],
                    states_explored=421,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                ),
            ),
            ScenarioStep(
                step_id=3,
                title=t["steps"][3]["title"],
                description=t["steps"][3]["description"],
                agent_action=t["steps"][3]["agent_action"],
                operations=[
                    AgentOperation(op_type="rolling_update", params={"service": "user-svc", "region": "east"}),
                    AgentOperation(op_type="scale_up", params={"service": "database", "region": "east", "amount": 1}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="rolling_update", params={"service": "user-svc", "region": "east"}),
                        AgentOperation(op_type="scale_up", params={"service": "database", "region": "east", "amount": 1}),
                    ],
                    properties_checked=["NoSimultaneousUpdatesOnChain", "AvailabilityFloor"],
                    violations=[
                        PropertyViolation(
                            property_name="NoSimultaneousUpdatesOnChain",
                            description=t["violations"]["NoSimultaneousUpdatesOnChain"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"user-svc.east": "running", "database.east": "running"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"user-svc.east": "deploying", "database.east": "running"}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"user-svc.east": "deploying", "database.east": "deploying"}, violated_property="NoSimultaneousUpdatesOnChain"),
                            ],
                        ),
                    ],
                    states_explored=8923,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"user-svc.east": "running(3)", "database.east": "running(1)"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"user-svc.east": "deploying(3)", "database.east": "running(1)"}, violated_property=None),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"user-svc.east": "deploying(3)", "database.east": "deploying(2)"}, violated_property="NoSimultaneousUpdatesOnChain"),
                    ],
                ),
            ),
        ],
        tla_spec=t["tla_spec"],
    )


def _scenario_5(L: dict) -> Scenario:
    t = L["scenario-5"]
    base = _base_state()

    s1_post = _clone(base)
    s1_post.services["inventory-svc"].replicas["east"] = 1

    s2_post = _clone(s1_post)
    s2_post.services["inventory-svc"].replicas["east"] = 0
    s2_post.services["inventory-svc"].state["east"] = ServiceState.DOWN

    spec_refs = _build_spec_refs(t)

    return Scenario(
        id="scenario-5",
        title=t["title"],
        subtitle=t["subtitle"],
        description=t["description"],
        constraints=_build_constraints(t),
        initial_state=base,
        steps=[
            ScenarioStep(
                step_id=1,
                title=t["steps"][1]["title"],
                description=t["steps"][1]["description"],
                agent_action=t["steps"][1]["agent_action"],
                operations=[
                    AgentOperation(op_type="scale_down", params={"service": "inventory-svc", "region": "east", "amount": 1, "reason": "cost_optimization"}),
                ],
                pre_state=base,
                post_state=s1_post,
                verification=VerificationReport(
                    result=VerificationResult.UNSAFE,
                    operations_checked=[
                        AgentOperation(op_type="scale_down", params={"service": "inventory-svc", "region": "east", "amount": 1}),
                    ],
                    properties_checked=["MinimumRedundancy", "AvailabilityFloor", "NoCyclicDependencies"],
                    violations=[
                        PropertyViolation(
                            property_name="MinimumRedundancy",
                            description=t["violations"]["MinimumRedundancy"],
                            severity="critical",
                            trace=[
                                TraceStep(step=1, description=t["trace"][1], state_snapshot={"inventory-svc.east": "running(2)", "critical_path": "healthy"}, violated_property=None),
                                TraceStep(step=2, description=t["trace"][2], state_snapshot={"inventory-svc.east": "running(1)", "critical_path": "healthy but fragile"}, violated_property=None),
                                TraceStep(step=3, description=t["trace"][3], state_snapshot={"inventory-svc.east": "down(0)", "critical_path": "BROKEN"}, violated_property="MinimumRedundancy"),
                                TraceStep(step=4, description=t["trace"][4], state_snapshot={"order-svc": "unhealthy (dep down)", "pay-svc": "cannot verify inventory"}, violated_property="AvailabilityFloor"),
                            ],
                        ),
                    ],
                    states_explored=5621,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
                    tla_spec_refs=spec_refs,
                    counterexample_trace=[
                        TraceStep(step=1, description=t["counterexample"][1], state_snapshot={"inventory-svc.east.replicas": 2, "inventory-svc.east.state": "running"}, violated_property=None),
                        TraceStep(step=2, description=t["counterexample"][2], state_snapshot={"inventory-svc.east.replicas": 1, "inventory-svc.east.state": "running"}, violated_property=None),
                        TraceStep(step=3, description=t["counterexample"][3], state_snapshot={"inventory-svc.east.replicas": 0, "inventory-svc.east.state": "down"}, violated_property="MinimumRedundancy"),
                    ],
                ),
            ),
            ScenarioStep(
                step_id=2,
                title=t["steps"][2]["title"],
                description=t["steps"][2]["description"],
                agent_action=t["steps"][2]["agent_action"],
                operations=[],
                pre_state=s1_post,
                post_state=base,
                verification=VerificationReport(
                    result=VerificationResult.SAFE,
                    operations_checked=[],
                    properties_checked=["MinimumRedundancy"],
                    violations=[],
                    states_explored=5621,
                    tla_spec_used="SREInfrastructure.tla + Properties.tla",
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
        {"id": sid, "title": L[sid]["title"], "subtitle": L[sid]["subtitle"]}
        for sid in _BUILDERS
    ]
