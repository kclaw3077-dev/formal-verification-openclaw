"""
Data models for the SRE Infrastructure and Agent operations.
"""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


class ServiceState(str, Enum):
    RUNNING = "running"
    DEPLOYING = "deploying"
    DEGRADED = "degraded"
    DOWN = "down"


class VerificationResult(str, Enum):
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    UNKNOWN = "UNKNOWN"


class Region(str, Enum):
    EAST = "east"
    WEST = "west"


class ServiceInfo(BaseModel):
    name: str
    replicas: dict[str, int]  # region -> count
    state: dict[str, ServiceState]  # region -> state
    dependencies: list[str]
    is_critical: bool = False


class InfrastructureState(BaseModel):
    services: dict[str, ServiceInfo]
    active_region: str
    db_write_region: str


class AgentOperation(BaseModel):
    op_type: str  # rolling_update, scale_down, scale_up, add_dep, switch_traffic, switch_db_writes
    params: dict


class PropertyViolation(BaseModel):
    property_name: str
    description: str
    severity: str  # critical, warning
    trace: list[TraceStep] = []


class TraceStep(BaseModel):
    step: int
    description: str
    state_snapshot: dict
    violated_property: str | None = None


# Fix forward reference
PropertyViolation.model_rebuild()


class TlaSpecRef(BaseModel):
    filename: str         # "SREInfrastructure.tla"
    defines: list[str]    # ["Services", "RollingUpdate", "EffectiveCapacity"]
    relevant_section: str # why this spec matters for this step


class VerificationReport(BaseModel):
    result: VerificationResult
    operations_checked: list[AgentOperation]
    properties_checked: list[str]
    violations: list[PropertyViolation]
    states_explored: int
    tla_spec_used: str
    tla_spec_refs: list[TlaSpecRef] = []
    counterexample_trace: list[TraceStep] = []


class ConstraintDef(BaseModel):
    name: str          # "AvailabilityFloor"
    expression: str    # TLA+ expression
    threshold: str     # "66%"
    description: str   # human-readable explanation


class ScenarioStep(BaseModel):
    step_id: int
    title: str
    description: str
    agent_action: str
    operations: list[AgentOperation]
    pre_state: InfrastructureState | None = None
    post_state: InfrastructureState | None = None
    verification: VerificationReport | None = None


class Scenario(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    constraints: list[ConstraintDef] = []
    initial_state: InfrastructureState
    steps: list[ScenarioStep]
    tla_spec: str  # The TLA+ specification text relevant to this scenario
