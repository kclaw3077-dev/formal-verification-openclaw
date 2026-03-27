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
  "verification.realizable": "REALIZABLE",
  "verification.unrealizable": "UNREALIZABLE",
  "verification.safe.desc": "All invariants satisfied across all reachable states",
  "verification.unsafe.desc": "{count} property violation(s) found",
  "verification.realizable.desc": "All specifications can be simultaneously satisfied",
  "verification.unrealizable.desc": "Specifications contain inherent conflicts — {count} constraint(s) in conflict",
  "verification.propertiesChecked": "Properties Checked",
  "verification.violations": "Violations",
  "verification.conflictProof": "Conflicting Constraints",
  "verification.synthesizedController": "Synthesized Controller",

  // Trace
  "trace.empty": "No counterexample — all states safe.",
  "trace.violates": "Violates:",

  // Service states
  "state.running": "running",
  "state.deploying": "deploying",
  "state.degraded": "degraded",
  "state.down": "down",
  "state.cache_miss": "cache miss",

  // Constraints panel
  "constraints.title": "Verification Constraints",

  // Overview page — architecture pipeline
  "overview.title": "Formal Methods across the SRE Lifecycle",
  "overview.subtitle":
    "Four phases form a closed loop: define specs → synthesize controllers → verify at runtime → learn from incidents",

  "overview.pipeline.step1.title": "① Define Spec — Realizability Check",
  "overview.pipeline.step1.desc": "Verify that SLO specifications can be simultaneously satisfied before any implementation",
  "overview.pipeline.step1.example": "",

  "overview.pipeline.step2.title": "② Build Controller — Reactive Synthesis",
  "overview.pipeline.step2.desc": "Auto-generate a correct-by-construction execution strategy from safety specifications",
  "overview.pipeline.step2.example": "",

  "overview.pipeline.step3.title": "③ Runtime Ops — Bounded Model Checking",
  "overview.pipeline.step3.desc": "Verify each operation is safe within k steps before execution, catching compound failures",
  "overview.pipeline.step3.example": "",

  "overview.pipeline.step4.title": "④ Post-Incident — BMC Reverse + Feedback",
  "overview.pipeline.step4.desc": "Trace fault paths backward, discover new invariants, feed back to Phase ① for re-synthesis",
  "overview.pipeline.step4.example": "",

  "overview.pipeline.arrow.output": "Output:",

  // Overview page — lifecycle phases
  "overview.phases.title": "Four Lifecycle Phases",

  "overview.phase.realizability.title": "Phase ① Realizability Check",
  "overview.phase.realizability.description": "Verify specification consistency before building",
  "overview.phase.realizability.scenario.scenario-1": "SLO Conflict Detection",

  "overview.phase.synthesis.title": "Phase ② Reactive Synthesis",
  "overview.phase.synthesis.description": "Auto-generate correct controllers from specifications",
  "overview.phase.synthesis.scenario.scenario-2": "Elastic Strategy Synthesis",

  "overview.phase.bmc.title": "Phase ③ Runtime Verification",
  "overview.phase.bmc.description": "Verify changes and fault responses in real-time",
  "overview.phase.bmc.scenario.scenario-3": "Emergency Hotfix",
  "overview.phase.bmc.scenario.scenario-4": "Failover Split-Brain",

  "overview.phase.feedback.title": "Phase ④ → ① Feedback Loop",
  "overview.phase.feedback.description": "Post-incident analysis feeds back new specifications",
  "overview.phase.feedback.scenario.scenario-5": "Retrospective & Feedback",

  // Back to overview
  "nav.backToOverview": "Overview",

  // TLA+ spec references
  "tla.specFiles": "Spec Files",
  "tla.defines": "Defines:",
  "tla.relevance": "Relevant to this step:",
  "tla.specFilesChecked": "{count} spec file(s) checked",

  // Language toggle
  "lang.switch": "中文",
} as const;

export type LocaleKeys = keyof typeof en;
export default en;
