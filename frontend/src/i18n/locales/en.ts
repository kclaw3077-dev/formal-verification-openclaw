const en = {
  // Header
  "header.title": "Formal Verification Gate",
  "header.subtitle": "OpenClaw SRE Agent + TLA+ Model Checking",
  "header.badge.demo": "Demo",
  "header.badge.tla": "TLA+",

  // Sidebar
  "sidebar.title": "Scenarios",

  // Empty state
  "empty.title": "Select a Scenario",
  "empty.description":
    "Choose a scenario from the left to explore how TLA+ formal verification catches subtle issues in SRE operations before they reach production.",
  "loading": "Loading scenario...",

  // Panel titles
  "panel.topology": "Service Topology",
  "panel.verification": "Verification Result",
  "panel.trace": "Counterexample Trace",
  "panel.tlaSpec": "TLA+ Specification",

  // Scenario player
  "step.label": "Step",
  "step.agentAction": "Agent Action:",
  "step.statesExplored": "States explored:",
  "step.propertiesChecked": "Properties checked:",
  "step.spec": "Spec:",

  // Verification
  "verification.safe": "SAFE",
  "verification.unsafe": "UNSAFE",
  "verification.safe.desc": "All invariants satisfied across all reachable states",
  "verification.unsafe.desc": "{count} property violation(s) found",
  "verification.propertiesChecked": "Properties Checked",
  "verification.violations": "Violations",

  // Trace
  "trace.empty": "No counterexample \u2014 all states safe.",
  "trace.violates": "Violates:",

  // Service states
  "state.running": "running",
  "state.deploying": "deploying",
  "state.degraded": "degraded",
  "state.down": "down",

  // Constraints panel
  "constraints.title": "Verification Constraints",

  // Overview page — architecture pipeline
  "overview.title": "Agent Architecture with Formal Verification",
  "overview.subtitle":
    "Where does formal verification sit in the SRE Agent pipeline? What goes in, and what comes out?",

  "overview.pipeline.step1.title": "Natural Language Intent",
  "overview.pipeline.step1.desc": "User describes the operation in natural language",
  "overview.pipeline.step1.example": "\"Scale down inventory-svc to save costs at low traffic\"",

  "overview.pipeline.step2.title": "Agent LLM Reasoning",
  "overview.pipeline.step2.desc": "OpenClaw Agent parses intent, queries infra state, generates an execution plan",
  "overview.pipeline.step2.example": "Reads monitoring data, evaluates cost/risk, selects operation",

  "overview.pipeline.step3.title": "Structured Operation Plan",
  "overview.pipeline.step3.desc": "Agent outputs typed operation descriptors \u2014 NOT natural language",
  "overview.pipeline.step3.example": "AgentOperation(op_type=\"scale_down\", params={service, region, amount})\n+ Current InfrastructureState snapshot",

  "overview.pipeline.step4.title": "Formal Verification Gate (TLA+)",
  "overview.pipeline.step4.desc": "Maps operations + state into a TLA+ model, TLC model checker exhaustively explores all reachable states",
  "overview.pipeline.step4.example": "Input: TLA+ model parameters\nOutput: SAFE / UNSAFE + counterexample trace",

  "overview.pipeline.step5.title": "Execute or Reject",
  "overview.pipeline.step5.desc": "SAFE \u2192 execute the operation; UNSAFE \u2192 block and show the counterexample to the operator",
  "overview.pipeline.step5.example": "",

  "overview.pipeline.arrow.output": "Output:",

  // Overview page — verification modes
  "overview.modes.title": "Three Verification Modes",
  "overview.mode.single.title": "Single Operation",
  "overview.mode.single.description":
    "Check all reachable states after one operation, including failure scenarios",
  "overview.mode.single.scenario.scenario-1": "S1: Capacity Bottleneck",
  "overview.mode.single.scenario.scenario-2": "S2: Circular Dependency",
  "overview.mode.single.scenario.scenario-5": "S5: Scale-Down Cascade",
  "overview.mode.plan.title": "Plan Verification",
  "overview.mode.plan.description":
    "Check every intermediate state in a multi-step plan for race conditions",
  "overview.mode.plan.scenario.scenario-3": "S3: Split-Brain Failover",
  "overview.mode.concurrent.title": "Concurrent Operations",
  "overview.mode.concurrent.description":
    "Explore all interleavings of parallel operations to find dangerous combinations",
  "overview.mode.concurrent.scenario.scenario-4": "S4: Operations Conflict",

  // Back to overview
  "nav.backToOverview": "Overview",

  // TLA+ spec references
  "tla.specFiles": "Spec Files",
  "tla.defines": "Defines:",
  "tla.relevance": "Relevant to this step:",
  "tla.specFilesChecked": "{count} spec file(s) checked",

  // Language toggle
  "lang.switch": "\u4e2d\u6587",
} as const;

export type LocaleKeys = keyof typeof en;
export default en;
