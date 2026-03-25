const zh: Record<string, string> = {
  // Header
  "header.title": "\u5f62\u5f0f\u5316\u9a8c\u8bc1\u95e8\u7981",
  "header.subtitle": "OpenClaw SRE Agent + TLA+ \u6a21\u578b\u68c0\u67e5",
  "header.badge.demo": "\u6f14\u793a",
  "header.badge.tla": "TLA+",

  // Sidebar
  "sidebar.title": "\u573a\u666f\u5217\u8868",

  // Empty state
  "empty.title": "\u8bf7\u9009\u62e9\u4e00\u4e2a\u573a\u666f",
  "empty.description":
    "\u4ece\u5de6\u4fa7\u9009\u62e9\u4e00\u4e2a\u573a\u666f\uff0c\u63a2\u7d22 TLA+ \u5f62\u5f0f\u5316\u9a8c\u8bc1\u5982\u4f55\u5728\u8fd0\u7ef4\u64cd\u4f5c\u4e0a\u7ebf\u524d\u53d1\u73b0\u96be\u4ee5\u5bdf\u89c9\u7684\u9690\u60a3\u3002",
  "loading": "\u6b63\u5728\u52a0\u8f7d\u573a\u666f...",

  // Panel titles
  "panel.topology": "\u670d\u52a1\u62d3\u6251\u56fe",
  "panel.verification": "\u9a8c\u8bc1\u7ed3\u679c",
  "panel.trace": "\u53cd\u4f8b Trace",
  "panel.tlaSpec": "TLA+ \u89c4\u7ea6",

  // Scenario player
  "step.label": "\u6b65\u9aa4",
  "step.agentAction": "Agent \u64cd\u4f5c\uff1a",
  "step.statesExplored": "\u5df2\u63a2\u7d22\u72b6\u6001\u6570\uff1a",
  "step.propertiesChecked": "\u5df2\u68c0\u67e5\u5c5e\u6027\u6570\uff1a",
  "step.spec": "\u89c4\u7ea6\u6587\u4ef6\uff1a",

  // Verification
  "verification.safe": "\u5b89\u5168",
  "verification.unsafe": "\u4e0d\u5b89\u5168",
  "verification.safe.desc": "\u6240\u6709\u53ef\u8fbe\u72b6\u6001\u5747\u6ee1\u8db3\u5168\u90e8\u4e0d\u53d8\u91cf",
  "verification.unsafe.desc": "\u53d1\u73b0 {count} \u4e2a\u5c5e\u6027\u8fdd\u53cd",
  "verification.propertiesChecked": "\u5df2\u68c0\u67e5\u5c5e\u6027",
  "verification.violations": "\u8fdd\u53cd\u8be6\u60c5",

  // Trace
  "trace.empty": "\u65e0\u53cd\u4f8b \u2014 \u6240\u6709\u72b6\u6001\u5b89\u5168\u3002",
  "trace.violates": "\u8fdd\u53cd\uff1a",

  // Service states
  "state.running": "\u8fd0\u884c\u4e2d",
  "state.deploying": "\u90e8\u7f72\u4e2d",
  "state.degraded": "\u964d\u7ea7",
  "state.down": "\u5df2\u5b95\u673a",

  // Constraints panel
  "constraints.title": "\u9a8c\u8bc1\u7ea6\u675f\u6761\u4ef6",

  // Overview page — architecture pipeline
  "overview.title": "Agent \u67b6\u6784\u4e0e\u5f62\u5f0f\u5316\u9a8c\u8bc1",
  "overview.subtitle":
    "\u5f62\u5f0f\u5316\u9a8c\u8bc1\u5728 SRE Agent \u7ba1\u7ebf\u4e2d\u7684\u4f4d\u7f6e\u662f\u4ec0\u4e48\uff1f\u8f93\u5165\u662f\u4ec0\u4e48\uff0c\u8f93\u51fa\u662f\u4ec0\u4e48\uff1f",

  "overview.pipeline.step1.title": "\u81ea\u7136\u8bed\u8a00\u610f\u56fe",
  "overview.pipeline.step1.desc": "\u7528\u6237\u7528\u81ea\u7136\u8bed\u8a00\u63cf\u8ff0\u8fd0\u7ef4\u64cd\u4f5c",
  "overview.pipeline.step1.example": "\"\u51cc\u6668\u6d41\u91cf\u4f4e\uff0c\u5e2e\u6211\u7f29\u5bb9 inventory-svc \u8282\u7ea6\u6210\u672c\"",

  "overview.pipeline.step2.title": "Agent LLM \u63a8\u7406",
  "overview.pipeline.step2.desc": "OpenClaw Agent \u89e3\u6790\u610f\u56fe\uff0c\u67e5\u8be2\u57fa\u7840\u8bbe\u65bd\u72b6\u6001\uff0c\u751f\u6210\u6267\u884c\u8ba1\u5212",
  "overview.pipeline.step2.example": "\u8bfb\u53d6\u76d1\u63a7\u6570\u636e\uff0c\u8bc4\u4f30\u6210\u672c/\u98ce\u9669\uff0c\u9009\u62e9\u64cd\u4f5c\u7c7b\u578b",

  "overview.pipeline.step3.title": "\u7ed3\u6784\u5316\u64cd\u4f5c\u8ba1\u5212",
  "overview.pipeline.step3.desc": "Agent \u8f93\u51fa\u7c7b\u578b\u5316\u7684\u64cd\u4f5c\u63cf\u8ff0\u7b26\u2014\u2014\u4e0d\u662f\u81ea\u7136\u8bed\u8a00",
  "overview.pipeline.step3.example": "AgentOperation(op_type=\"scale_down\", params={service, region, amount})\n+ \u5f53\u524d InfrastructureState \u5feb\u7167",

  "overview.pipeline.step4.title": "\u5f62\u5f0f\u5316\u9a8c\u8bc1\u95e8\u7981 (TLA+)",
  "overview.pipeline.step4.desc": "\u5c06\u64cd\u4f5c + \u72b6\u6001\u6620\u5c04\u4e3a TLA+ \u6a21\u578b\uff0cTLC \u6a21\u578b\u68c0\u67e5\u5668\u7a77\u4e3e\u63a2\u7d22\u6240\u6709\u53ef\u8fbe\u72b6\u6001",
  "overview.pipeline.step4.example": "\u8f93\u5165\uff1aTLA+ \u6a21\u578b\u53c2\u6570\n\u8f93\u51fa\uff1aSAFE / UNSAFE + \u53cd\u4f8b trace",

  "overview.pipeline.step5.title": "\u6267\u884c / \u62d2\u7edd",
  "overview.pipeline.step5.desc": "SAFE \u2192 \u6267\u884c\u64cd\u4f5c\uff1bUNSAFE \u2192 \u62e6\u622a\u5e76\u5411\u8fd0\u7ef4\u4eba\u5458\u5c55\u793a\u53cd\u4f8b",
  "overview.pipeline.step5.example": "",

  "overview.pipeline.arrow.output": "\u8f93\u51fa\uff1a",

  // Overview page — verification modes
  "overview.modes.title": "\u4e09\u79cd\u9a8c\u8bc1\u6a21\u5f0f",
  "overview.mode.single.title": "\u5355\u64cd\u4f5c\u9a8c\u8bc1",
  "overview.mode.single.description":
    "\u68c0\u67e5\u4e00\u4e2a\u64cd\u4f5c\u540e\u7684\u6240\u6709\u53ef\u8fbe\u72b6\u6001\uff0c\u5305\u62ec\u6545\u969c\u573a\u666f",
  "overview.mode.single.scenario.scenario-1": "S1: \u5bb9\u91cf\u74f6\u9888",
  "overview.mode.single.scenario.scenario-2": "S2: \u5faa\u73af\u4f9d\u8d56",
  "overview.mode.single.scenario.scenario-5": "S5: \u7f29\u5bb9\u7ea7\u8054",
  "overview.mode.plan.title": "\u8ba1\u5212\u9a8c\u8bc1",
  "overview.mode.plan.description":
    "\u68c0\u67e5\u591a\u6b65\u8ba1\u5212\u7684\u6bcf\u4e2a\u4e2d\u95f4\u72b6\u6001\uff0c\u6355\u6349\u7ade\u6001\u6761\u4ef6",
  "overview.mode.plan.scenario.scenario-3": "S3: \u8111\u88c2\u5207\u6362",
  "overview.mode.concurrent.title": "\u5e76\u53d1\u64cd\u4f5c\u9a8c\u8bc1",
  "overview.mode.concurrent.description":
    "\u63a2\u7d22\u5e76\u884c\u64cd\u4f5c\u7684\u6240\u6709\u4ea4\u9519\u5e8f\u5217\uff0c\u53d1\u73b0\u5371\u9669\u7ec4\u5408",
  "overview.mode.concurrent.scenario.scenario-4": "S4: \u64cd\u4f5c\u51b2\u7a81",

  // Back to overview
  "nav.backToOverview": "\u6982\u89c8",

  // TLA+ spec references
  "tla.specFiles": "\u89c4\u7ea6\u6587\u4ef6",
  "tla.defines": "\u5b9a\u4e49\uff1a",
  "tla.relevance": "\u4e0e\u6b64\u6b65\u9aa4\u7684\u5173\u8054\uff1a",
  "tla.specFilesChecked": "\u5df2\u68c0\u67e5 {count} \u4e2a\u89c4\u7ea6\u6587\u4ef6",

  // Language toggle
  "lang.switch": "EN",
};

export default zh;
