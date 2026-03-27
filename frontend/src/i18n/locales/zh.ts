const zh: Record<string, string> = {
  // Header
  "header.title": "SRE 验证门禁",
  "header.subtitle": "OpenClaw SRE Agent — 形式化保证引擎",
  "header.badge.demo": "演示",
  "header.badge.tla": "TLA+",

  // Sidebar
  "sidebar.title": "场景列表",

  // Empty state
  "empty.title": "请选择一个场景",
  "empty.description":
    "从左侧选择一个场景，探索自动化安全保证如何在运维操作上线前发现难以察觉的隐患。",
  "loading": "正在加载场景...",

  // Panel titles
  "panel.topology": "服务拓扑图",
  "panel.verification": "保证详情",
  "panel.trace": "故障路径",
  "panel.tlaSpec": "形式化规约",

  // Scenario player
  "step.label": "步骤",
  "step.agentAction": "Agent 操作：",
  "step.statesExplored": "已探索状态数：",
  "step.propertiesChecked": "已检查属性数：",
  "step.spec": "规约文件：",

  // SRE narrative labels
  "sre.context": "场景",
  "sre.keyQuestion": "关键问题",
  "sre.guarantee": "保证结果",
  "sre.detailToggle": "查看详细分析",
  "sre.detailToggleClose": "收起详情",
  "sre.fmBadge.realizability": "Realizability",
  "sre.fmBadge.synthesis": "Synthesis",
  "sre.fmBadge.bmc": "BMC",
  "sre.fmBadge.bmc_reverse": "BMC Reverse",

  // Verification
  "verification.safe": "可以保证",
  "verification.unsafe": "不能保证",
  "verification.realizable": "可满足",
  "verification.unrealizable": "不可满足",
  "verification.safe.desc": "所有可达状态均满足全部安全属性",
  "verification.unsafe.desc": "发现 {count} 个安全问题",
  "verification.realizable.desc": "所有规约可以同时满足",
  "verification.unrealizable.desc": "规约存在内在冲突 — {count} 条约束冲突",
  "verification.propertiesChecked": "已检查属性",
  "verification.violations": "问题详情",
  "verification.conflictProof": "冲突约束",
  "verification.synthesizedController": "生成的控制器",

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
  "overview.title": "SRE 生命周期中的安全保证",
  "overview.subtitle":
    "四阶段闭环：定义 SLO → 生成执行策略 → 验证操作安全 → 从事故中学习",

  "overview.pipeline.step1.title": "① 定义 SLO — 目标能同时满足吗？",
  "overview.pipeline.step1.desc": "在实施前，验证你的 SLO 目标在当前部署拓扑下是否互相冲突",
  "overview.pipeline.step1.example": "",

  "overview.pipeline.step2.title": "② 生成执行策略 — 自动化是否可靠？",
  "overview.pipeline.step2.desc": "从安全要求自动生成正确的执行策略，发现人工难以穷举的隐藏约束",
  "overview.pipeline.step2.example": "",

  "overview.pipeline.step3.title": "③ 变更与应急 — 这步操作安全吗？",
  "overview.pipeline.step3.desc": "执行前验证每个操作在最坏复合故障下是否仍满足安全阈值",
  "overview.pipeline.step3.example": "",

  "overview.pipeline.step4.title": "④ 事后复盘 — 如何防止复发？",
  "overview.pipeline.step4.desc": "追踪故障路径，发现缺失的安全不变量，反馈至 ① 加固系统",
  "overview.pipeline.step4.example": "",

  "overview.pipeline.arrow.output": "输出：",

  // Overview page — lifecycle phases
  "overview.phases.title": "探索场景",

  "overview.phase.realizability.title": "① 定义 SLO",
  "overview.phase.realizability.description": "你的 SLO 目标能同时满足吗？",
  "overview.phase.realizability.scenario.scenario-1": "SLO 冲突检测",

  "overview.phase.synthesis.title": "② 生成执行策略",
  "overview.phase.synthesis.description": "自动生成可靠的弹性伸缩策略",
  "overview.phase.synthesis.scenario.scenario-2": "弹性伸缩策略",

  "overview.phase.bmc.title": "③ 运行时保证",
  "overview.phase.bmc.description": "这次变更/切换安全吗？",
  "overview.phase.bmc.scenario.scenario-3": "紧急热修复",
  "overview.phase.bmc.scenario.scenario-4": "Failover 脑裂",

  "overview.phase.feedback.title": "④ 事后复盘",
  "overview.phase.feedback.description": "从事故中学习，防止复发",
  "overview.phase.feedback.scenario.scenario-5": "故障回溯与闭环",

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
