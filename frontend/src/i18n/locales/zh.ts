const zh: Record<string, string> = {
  // Header
  "header.title": "形式化验证门禁",
  "header.subtitle": "OpenClaw SRE Agent + TLA+ 模型检查",
  "header.badge.demo": "演示",
  "header.badge.tla": "TLA+",

  // Sidebar
  "sidebar.title": "场景列表",

  // Empty state
  "empty.title": "请选择一个场景",
  "empty.description":
    "从左侧选择一个场景，探索 TLA+ 形式化验证如何在运维操作上线前发现难以察觉的隐患。",
  "loading": "正在加载场景...",

  // Panel titles
  "panel.topology": "服务拓扑图",
  "panel.verification": "验证结果",
  "panel.trace": "反例 Trace",
  "panel.tlaSpec": "TLA+ 规约",

  // Scenario player
  "step.label": "步骤",
  "step.agentAction": "Agent 操作：",
  "step.statesExplored": "已探索状态数：",
  "step.propertiesChecked": "已检查属性数：",
  "step.spec": "规约文件：",

  // Verification
  "verification.safe": "安全",
  "verification.unsafe": "不安全",
  "verification.realizable": "可实现",
  "verification.unrealizable": "不可实现",
  "verification.safe.desc": "所有可达状态均满足全部不变量",
  "verification.unsafe.desc": "发现 {count} 个属性违反",
  "verification.realizable.desc": "所有规约可以同时满足",
  "verification.unrealizable.desc": "规约存在内在冲突 — {count} 条约束冲突",
  "verification.propertiesChecked": "已检查属性",
  "verification.violations": "违反详情",
  "verification.conflictProof": "冲突约束",
  "verification.synthesizedController": "合成控制器",

  // Trace
  "trace.empty": "无反例 — 所有状态安全。",
  "trace.violates": "违反：",

  // Service states
  "state.running": "运行中",
  "state.deploying": "部署中",
  "state.degraded": "降级",
  "state.down": "已宕机",
  "state.cache_miss": "缓存未命中",

  // Constraints panel
  "constraints.title": "验证约束条件",

  // Overview page — architecture pipeline
  "overview.title": "形式化方法在 SRE 生命周期中的应用",
  "overview.subtitle":
    "四阶段闭环：定义规约 → 合成控制器 → 运行时验证 → 事后复盘",

  "overview.pipeline.step1.title": "① 定义规约 — 可实现性检查",
  "overview.pipeline.step1.desc": "在任何实现之前，验证 SLO 规约能否同时满足",
  "overview.pipeline.step1.example": "",

  "overview.pipeline.step2.title": "② 构建控制器 — 反应式合成",
  "overview.pipeline.step2.desc": "从安全规约自动生成构造正确的执行策略",
  "overview.pipeline.step2.example": "",

  "overview.pipeline.step3.title": "③ 运行时运维 — 有界模型检查",
  "overview.pipeline.step3.desc": "在执行前验证每个操作在 k 步内是安全的，捕获复合故障",
  "overview.pipeline.step3.example": "",

  "overview.pipeline.step4.title": "④ 事后复盘 — BMC 反向追踪 + 反馈",
  "overview.pipeline.step4.desc": "反向追踪故障路径，发现新不变量，反馈至阶段①进行重新合成",
  "overview.pipeline.step4.example": "",

  "overview.pipeline.arrow.output": "输出：",

  // Overview page — lifecycle phases
  "overview.phases.title": "四个生命周期阶段",

  "overview.phase.realizability.title": "阶段 ① 可实现性检查",
  "overview.phase.realizability.description": "在构建前验证规约一致性",
  "overview.phase.realizability.scenario.scenario-1": "SLO 冲突检测",

  "overview.phase.synthesis.title": "阶段 ② 反应式合成",
  "overview.phase.synthesis.description": "从规约自动生成正确的控制器",
  "overview.phase.synthesis.scenario.scenario-2": "弹性策略合成",

  "overview.phase.bmc.title": "阶段 ③ 运行时验证",
  "overview.phase.bmc.description": "实时验证变更和故障响应",
  "overview.phase.bmc.scenario.scenario-3": "紧急热修复",
  "overview.phase.bmc.scenario.scenario-4": "故障切换脑裂",

  "overview.phase.feedback.title": "阶段 ④ → ① 反馈闭环",
  "overview.phase.feedback.description": "事后分析反馈新规约",
  "overview.phase.feedback.scenario.scenario-5": "复盘与反馈",

  // Back to overview
  "nav.backToOverview": "概览",

  // TLA+ spec references
  "tla.specFiles": "规约文件",
  "tla.defines": "定义：",
  "tla.relevance": "与此步骤的关联：",
  "tla.specFilesChecked": "已检查 {count} 个规约文件",

  // Language toggle
  "lang.switch": "EN",
};

export default zh;
