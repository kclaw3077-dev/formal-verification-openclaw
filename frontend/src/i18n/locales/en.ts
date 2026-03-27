const en = {
  // Header
  "header.title": "SRE Verification Gate",
  "header.subtitle": "OpenClaw SRE Agent — Formal Guarantee Engine",
  "header.badge.demo": "Demo",
  "header.badge.tla": "TLA+",

  // Sidebar
  "sidebar.title": "Scenarios",

  // Empty state
  "empty.title": "Select a Scenario",
  "empty.description":
    "Choose a scenario from the left to explore how automated safety guarantees protect SRE operations before they reach production.",
  "loading": "Loading scenario...",

  // Panel titles
  "panel.topology": "Service Topology",
  "panel.verification": "Guarantee Details",
  "panel.trace": "Fault Path",
  "panel.tlaSpec": "Formal Specification",

  // Scenario player
  "step.label": "Step",
  "step.agentAction": "Agent Action:",
  "step.statesExplored": "States explored:",
  "step.propertiesChecked": "Properties checked:",
  "step.spec": "Spec:",

  // SRE narrative labels
  "sre.context": "Scenario",
  "sre.keyQuestion": "Key Question",
  "sre.guarantee": "Guarantee",
  "sre.detailToggle": "View detailed analysis",
  "sre.detailToggleClose": "Collapse details",
  "sre.fmBadge.realizability": "Realizability",
  "sre.fmBadge.synthesis": "Synthesis",
  "sre.fmBadge.bmc": "BMC",
  "sre.fmBadge.bmc_reverse": "BMC Reverse",

  // Verification
  "verification.safe": "Can Guarantee",
  "verification.unsafe": "Cannot Guarantee",
  "verification.realizable": "Satisfiable",
  "verification.unrealizable": "Not Satisfiable",
  "verification.safe.desc": "All safety properties hold under all reachable states",
  "verification.unsafe.desc": "{count} safety issue(s) found",
  "verification.realizable.desc": "All specifications can be simultaneously satisfied",
  "verification.unrealizable.desc": "Specifications contain inherent conflicts — {count} constraint(s) in conflict",
  "verification.propertiesChecked": "Properties Checked",
  "verification.violations": "Issue Details",
  "verification.conflictProof": "Conflicting Constraints",
  "verification.synthesizedController": "Generated Controller",

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
  "overview.title": "Safety Guarantees across the SRE Lifecycle",
  "overview.subtitle":
    "Four phases form a closed loop: define SLOs → generate strategy → verify operations → learn from incidents",

  "overview.pipeline.step1.title": "① Define SLOs — Can they be satisfied?",
  "overview.pipeline.step1.desc": "Before implementation, verify that your SLO targets don't conflict under the current deployment topology",
  "overview.pipeline.step1.example": "",

  "overview.pipeline.step2.title": "② Build Strategy — Is automation reliable?",
  "overview.pipeline.step2.desc": "Auto-generate a correct execution strategy from safety requirements, discovering hidden constraints",
  "overview.pipeline.step2.example": "",

  "overview.pipeline.step3.title": "③ Changes & Incidents — Is this operation safe?",
  "overview.pipeline.step3.desc": "Before executing, verify each operation maintains safety under worst-case compound failures",
  "overview.pipeline.step3.example": "",

  "overview.pipeline.step4.title": "④ Post-Incident — How to prevent recurrence?",
  "overview.pipeline.step4.desc": "Trace fault paths, discover missing safety invariants, feed back to ① to strengthen the system",
  "overview.pipeline.step4.example": "",

  "overview.pipeline.arrow.output": "Output:",

  // Overview page — lifecycle phases
  "overview.phases.title": "Explore Scenarios",

  "overview.phase.realizability.title": "① Define SLOs",
  "overview.phase.realizability.description": "Can your SLO targets be met simultaneously?",
  "overview.phase.realizability.scenario.scenario-1": "SLO Conflict Detection",

  "overview.phase.synthesis.title": "② Build Strategy",
  "overview.phase.synthesis.description": "Auto-generate a reliable execution strategy",
  "overview.phase.synthesis.scenario.scenario-2": "Elastic Scaling Strategy",

  "overview.phase.bmc.title": "③ Runtime Guarantee",
  "overview.phase.bmc.description": "Is this change / failover safe to execute?",
  "overview.phase.bmc.scenario.scenario-3": "Emergency Hotfix",
  "overview.phase.bmc.scenario.scenario-4": "Failover Split-Brain",

  "overview.phase.feedback.title": "④ Post-Incident",
  "overview.phase.feedback.description": "Learn from incidents and prevent recurrence",
  "overview.phase.feedback.scenario.scenario-5": "Fault Retrospective",

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
