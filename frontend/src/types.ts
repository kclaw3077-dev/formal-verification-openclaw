export type ServiceState = "running" | "deploying" | "degraded" | "down";
export type VerificationResult = "SAFE" | "UNSAFE" | "UNKNOWN" | "REALIZABLE" | "UNREALIZABLE";

export interface ServiceInfo {
  name: string;
  replicas: Record<string, number>;
  state: Record<string, ServiceState>;
  dependencies: string[];
  is_critical: boolean;
  metrics?: Record<string, number> | null;
}

export interface InfrastructureState {
  services: Record<string, ServiceInfo>;
  active_region: string;
  db_write_region: string;
}

export interface AgentOperation {
  op_type: string;
  params: Record<string, unknown>;
}

export interface TraceStep {
  step: number;
  description: string;
  state_snapshot: Record<string, unknown>;
  violated_property: string | null;
}

export interface PropertyViolation {
  property_name: string;
  description: string;
  severity: string;
  trace: TraceStep[];
}

export interface TlaSpecRef {
  filename: string;
  defines: string[];
  relevant_section: string;
}

export interface VerificationReport {
  result: VerificationResult;
  operations_checked: AgentOperation[];
  properties_checked: string[];
  violations: PropertyViolation[];
  states_explored: number;
  tla_spec_used: string;
  tla_spec_refs: TlaSpecRef[];
  counterexample_trace: TraceStep[];
  synthesized_controller?: Record<string, unknown> | null;
  conflict_proof?: string[] | null;
}

export interface ScenarioStep {
  step_id: number;
  title: string;
  description: string;
  agent_action: string;
  operations: AgentOperation[];
  pre_state: InfrastructureState | null;
  post_state: InfrastructureState | null;
  verification: VerificationReport | null;
  // SRE-first narrative fields
  sre_context?: string;
  key_question?: string;
  guarantee?: string;
}

export interface ConstraintDef {
  name: string;
  expression: string;
  threshold: string;
  description: string;
}

export interface Scenario {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  constraints: ConstraintDef[];
  initial_state: InfrastructureState;
  steps: ScenarioStep[];
  tla_spec: string;
  phase?: string;
}

export interface ScenarioSummary {
  id: string;
  title: string;
  subtitle: string;
  phase?: string;
}
