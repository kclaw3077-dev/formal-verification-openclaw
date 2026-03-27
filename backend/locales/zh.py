"""Chinese locale — all user-facing scenario text."""

SCENARIOS = {
    # ── 场景 1 ──────────────────────────────────────────────────────────
    "scenario-1": {
        "phase": "① 定义 SLO",
        "title": "规约冲突检测",
        "subtitle": "大促前规约验证",
        "description": (
            "大促前，SRE 团队为支付链路定义三条 SLO：99.99% 可用性、P99 延迟 < 200ms、"
            "pay-svc 与 database 之间强一致性。Realizability Check 发现在当前双 AZ 部署下，"
            "三条规约不可同时满足。"
        ),
        "constraints": [
            {
                "name": "Availability_99_99",
                "expression": "Availability(pay-svc) >= 0.9999",
                "threshold": "99.99%",
                "description": "支付服务可用性必须达到 99.99%",
            },
            {
                "name": "LatencyP99_200ms",
                "expression": "P99Latency(pay-svc) <= 200",
                "threshold": "200ms",
                "description": "支付链路 P99 延迟必须低于 200ms",
            },
            {
                "name": "StrongConsistency",
                "expression": 'ConsistencyLevel(pay-svc, database) = "strong"',
                "threshold": "强一致",
                "description": "pay-svc 与 database 之间同步复制",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "SwitchTraffic", "SwitchDBWrites"],
                "relevant_section": "多区域服务模型与故障转移操作",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "AvailabilityFloor"],
                "relevant_section": "一致性与可用性不变量",
            },
        },
        "steps": {
            1: {
                "title": "定义支付链路 SLO",
                "description": (
                    "SRE 团队为支付关键路径定义三条同时要求：99.99% 可用性、"
                    "P99 延迟 < 200ms、强一致性。在双 AZ 部署下，强一致性要求跨 AZ 同步复制。"
                    "当一个 AZ 故障时，同步复制增加的延迟会将 P99 推至 200ms 以上，"
                    "迫使可用性降至 99.99% 以下。"
                ),
                "agent_action": "define_slo(availability=99.99%, latency_p99<200ms, consistency=strong)",
                "sre_context": "大促前，SRE 团队为支付链路定义三个 SLO：99.99% 可用性、P99 延迟 < 200ms、强一致性。系统采用双 AZ 部署（东区主、西区备）。",
                "key_question": "在当前双 AZ 部署下，这三个 SLO 能同时满足吗？",
                "guarantee": "❌ 不能保证。AZ 故障切换时，同步复制带来 150-300ms 跨区延迟，导致 P99 < 200ms 与强一致性、99.99% 可用性形成不可能三角。",
            },
            2: {
                "title": "放松规约",
                "description": (
                    "将强一致性调整为最终一致（有界过期）用于非关键读取。"
                    "支付写入保持强一致性，P99 放松至 500ms；"
                    "非关键查询路径使用最终一致性，P99 < 200ms。"
                    "重新检查确认放松后的规约集可实现。"
                ),
                "agent_action": "relax_spec(critical_path=strong+500ms, query_path=eventual+200ms)",
                "sre_context": "团队调整方案：支付写入保持强一致性但放宽 P99 至 500ms；非关键查询路径使用最终一致性，P99 < 200ms。",
                "key_question": "放宽后的规约组合能同时满足吗？",
                "guarantee": "✅ 可以保证。放宽后的规约不再冲突——强一致性仅适用于支付写入路径，该路径允许更高延迟。",
            },
        },
        "violations": {
            "RealizabilityConflict": (
                "在双 AZ 部署下，东区故障时，同步复制到西区增加 150-300ms 延迟。"
                "这使得在保持强一致性和 99.99% 可用性的同时无法满足 P99 < 200ms。"
                "这是 CAP 定理在具体部署拓扑上的体现。"
            ),
        },
        "trace": {
            1: "初始状态：双 AZ 部署，东区为主，启用同步复制",
            2: "东区数据库主节点发生网络分区",
            3: (
                "强一致性要求西区确认后才能提交写入 → 增加 150-300ms 跨 AZ 延迟 "
                "→ P99 超过 200ms → 必须拒绝写入以维持延迟 SLO → 可用性降至 99.99% 以下"
            ),
        },
        "counterexample": {
            1: "状态：{east: 主节点, west: 副本, sync_replication: true, all_healthy: true} — 三条 SLO 全部满足",
            2: "事件：东区网络分区 → 同步复制延迟升至 280ms",
            3: (
                "冲突：P99=280ms > 200ms 阈值。要维持 P99 < 200ms，必须拒绝慢写入 "
                "→ 可用性=99.91% < 99.99%。三条 SLO 在此拓扑下构成不可能三角。"
            ),
        },
        "tla_spec": (
            "--------------------------- MODULE RealizabilityCheck ---------------------------\n"
            "EXTENDS Integers, FiniteSets\n"
            "CONSTANTS Services, Regions, SyncLatencyMs\n"
            "VARIABLES activeRegion, dbWriteRegion, replicationMode, p99Latency, availability\n\n"
            "vars == <<activeRegion, dbWriteRegion, replicationMode, p99Latency, availability>>\n\n"
            "TypeOK ==\n"
            "    /\\ activeRegion \\in Regions\n"
            "    /\\ dbWriteRegion \\in Regions\n"
            "    /\\ replicationMode \\in {\"sync\", \"async\", \"bounded_staleness\"}\n"
            "    /\\ p99Latency \\in 0..1000\n"
            "    /\\ availability \\in 0..10000  \\* basis points (99.99% = 9999)\n\n"
            "Init ==\n"
            "    /\\ activeRegion = \"east\"\n"
            "    /\\ dbWriteRegion = \"east\"\n"
            "    /\\ replicationMode = \"sync\"\n"
            "    /\\ p99Latency = 50\n"
            "    /\\ availability = 9999\n\n"
            "RegionFailure(r) ==\n"
            "    /\\ r = activeRegion\n"
            "    /\\ IF replicationMode = \"sync\"\n"
            "       THEN /\\ p99Latency' = p99Latency + SyncLatencyMs\n"
            "            /\\ IF p99Latency' > 200\n"
            "               THEN availability' = availability - 8  \\* reject slow writes\n"
            "               ELSE availability' = availability\n"
            "       ELSE /\\ p99Latency' = p99Latency + 10\n"
            "            /\\ availability' = availability\n"
            "    /\\ UNCHANGED <<activeRegion, dbWriteRegion, replicationMode>>\n\n"
            "\\* The three SLOs — realizability requires all hold simultaneously\n"
            "SLO_Availability == availability >= 9999\n"
            "SLO_LatencyP99   == p99Latency <= 200\n"
            "SLO_Consistency  == replicationMode = \"sync\"\n\n"
            "AllSLOsSatisfied == SLO_Availability /\\ SLO_LatencyP99 /\\ SLO_Consistency\n"
            "=============================================================================\n"
        ),
    },

    # ── 场景 2 ──────────────────────────────────────────────────────────
    "scenario-2": {
        "phase": "② 生成执行策略",
        "title": "弹性策略合成",
        "subtitle": "自动生成正确的弹性控制器",
        "description": (
            "基于场景一修正后的规约，Reactive Synthesis 自动生成流量调度与弹性伸缩控制器。"
            "不再需要人工编写 SOP，合成器通过博弈求解产出 correct-by-construction 的状态机，"
            "发现了人工推演容易遗漏的约束条件。"
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "关键路径服务必须维持至少 66% 有效吞吐量",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "按服务配置",
                "description": "每个关键服务维持最小安全副本数",
            },
            {
                "name": "NoSimultaneousUpdatesOnChain",
                "expression": "\\A s,t : s->t => ~(deploying(s) /\\ deploying(t))",
                "threshold": "N/A",
                "description": "依赖链上的服务不能同时处于部署状态",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "serviceState", "RollingUpdate", "ScaleUp", "EffectiveCapacity"],
                "relevant_section": "服务状态转换模型与弹性伸缩操作",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                "relevant_section": "安全不变量集合，作为合成器的输入规约",
            },
        },
        "steps": {
            1: {
                "title": "输入规约到合成器",
                "description": (
                    "将环境模型（流量范围 1x-10x、单 AZ 最大 pod 数、AZ 故障概率）"
                    "和安全规约（AvailabilityFloor、MinimumRedundancy、"
                    "NoSimultaneousUpdatesOnChain）输入反应式合成引擎。"
                ),
                "agent_action": "synthesize(env_model={traffic:1x-10x, max_pods:20}, safety_specs=[AvailabilityFloor, MinimumRedundancy, NoSimultaneousUpdatesOnChain])",
                "sre_context": "基于场景 1 验证过的 SLO，团队需要为大促准备自动弹性伸缩策略。流量预计从 1x 飙升到 10x。团队不想手写 runbook，而是输入安全要求让系统自动生成正确的策略。",
                "key_question": "能否自动生成一个在 1x-10x 任意流量下都满足所有安全约束的伸缩策略？",
                "guarantee": "✅ 可以生成。合成引擎接受环境模型和安全规约，开始博弈求解。",
            },
            2: {
                "title": "发现互斥约束",
                "description": (
                    "合成器通过博弈论分析发现关键约束：当流量超过 8 倍时，扩缩容与滚动更新互斥。"
                    "在 8 倍流量下，滚动更新期间的 EffectiveCapacity 恰好降至 AvailabilityFloor 边界。"
                    "任何并发的扩缩容操作会进一步临时降低容量，违反安全下限。"
                ),
                "agent_action": "synthesis_result: guard(traffic > 8x → mutex(scale, rolling_update))",
                "sre_context": "策略生成过程中发现一个关键约束：当流量超过 8x 时，扩容和滚动更新操作互斥。在 8x 流量下，滚动更新期间的有效容量恰好压线可用性阈值——任何并发扩容都会突破安全线。",
                "key_question": "极端流量下，扩容与部署操作之间是否存在隐藏的互斥约束？",
                "guarantee": "✅ 发现隐藏约束：流量 > 8x 时扩容和滚动更新互斥。此约束原始 runbook 中未记录，如遗漏很可能导致大促事故。",
            },
            3: {
                "title": "生成完整控制器",
                "description": (
                    "合成器输出完整的状态机，包含所有守卫条件：inventory-svc 必须先于 "
                    "order-svc 扩容（瓶颈优先）、单 AZ 故障转移必须先切写入再切流量（防脑裂）、"
                    "以及 8 倍流量互斥守卫。控制器是 correct-by-construction 的。"
                ),
                "agent_action": "output: StateMachine(states=4, transitions=12, guards=6)",
                "sre_context": "完整的弹性控制器以状态机形式生成，包含 4 条守卫规则，覆盖所有流量区间。包括 8x 互斥约束、依赖排序扩容（inventory 先于 order）、滚动更新前容量预检查。",
                "key_question": "生成的控制器能否处理所有可能的流量模式并保持安全不变量？",
                "guarantee": "✅ 正确性由构造保证。控制器包含 5 个状态、8 条转换、4 条守卫。每个可达状态都满足所有安全属性。",
            },
        },
        "violations": {},
        "trace": {
            1: "合成引擎探索环境模型：traffic ∈ {1x, 2x, 4x, 8x, 10x}",
            2: "在 traffic=8x 时：滚动更新期间 EffectiveCapacity = MinSafeReplicas × 0.66 — 恰好在边界",
            3: "在 traffic=8x + 并发扩容时：pod 初始化期间临时容量下降 → EffectiveCapacity < AvailabilityFloor",
            4: "合成器添加守卫：traffic_multiplier <= 8 ∨ ¬rolling_update_in_progress",
        },
        "counterexample": {},
        "tla_spec": (
            "--------------------------- MODULE ReactiveSynthesis ---------------------------\n"
            "EXTENDS Integers, FiniteSets\n"
            "CONSTANTS Services, Regions, MaxPods, TrafficLevels\n"
            "VARIABLES serviceState, replicaCount, trafficMultiplier, controllerState\n\n"
            "vars == <<serviceState, replicaCount, trafficMultiplier, controllerState>>\n\n"
            "EffectiveCapacity(s) ==\n"
            "    LET running == {r \\in Regions : serviceState[s][r] = \"running\"}\n"
            "        deploying == {r \\in Regions : serviceState[s][r] = \"deploying\"}\n"
            "    IN  Cardinality(running) + Cardinality(deploying) \\div 2\n\n"
            "\\* Safety specifications (input to synthesizer)\n"
            "AvailabilityFloor ==\n"
            "    \\A s \\in Services :\n"
            "        EffectiveCapacity(s) * 2 >= replicaCount[s]\n\n"
            "\\* Synthesized guard: mutex at high traffic\n"
            "SynthesizedGuard_HighTrafficMutex ==\n"
            "    trafficMultiplier > 8 =>\n"
            "        ~(\\E s \\in Services :\n"
            "            /\\ serviceState[s][\"east\"] = \"deploying\"\n"
            "            /\\ controllerState = \"scaling\")\n\n"
            "\\* Synthesized guard: bottleneck-first scaling order\n"
            "SynthesizedGuard_BottleneckFirst ==\n"
            "    \\A s, t \\in Services :\n"
            "        (s # t /\\ EffectiveCapacity(s) < EffectiveCapacity(t)) =>\n"
            "            controllerState # \"scale_\" \\o t\n\n"
            "ControllerCorrectness ==\n"
            "    /\\ AvailabilityFloor\n"
            "    /\\ SynthesizedGuard_HighTrafficMutex\n"
            "    /\\ SynthesizedGuard_BottleneckFirst\n"
            "=============================================================================\n"
        ),
    },

    # ── 场景 3 ──────────────────────────────────────────────────────────
    "scenario-3": {
        "phase": "③ 运行时保证",
        "title": "变更验证——紧急 Hotfix",
        "subtitle": "部署前安全检查发现复合故障",
        "description": (
            "大促前一天，inventory-svc 发现库存扣减并发 bug，需要紧急滚动更新。"
            "当前已为大促扩容至 4 副本（东 2 西 2）。Agent 提议标准滚动更新，"
            "但 BMC 发现了一个危险的复合故障场景。"
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "关键路径服务必须维持至少 66% 有效吞吐量",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "按服务配置",
                "description": "每个关键服务维持最小安全副本数",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "serviceState", "RollingUpdate", "ReplicaFailure", "EffectiveCapacity"],
                "relevant_section": "建模滚动更新与副本降级的复合状态转换",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "MinimumRedundancy"],
                "relevant_section": "AvailabilityFloor 在复合故障场景下捕获链路吞吐量降至安全下限以下",
            },
        },
        "steps": {
            1: {
                "title": "Agent 提议滚动更新",
                "description": (
                    "Agent 对 inventory-svc（4 副本：东 2 西 2）提议滚动更新。"
                    "BMC 在 3 步内穷举所有可达状态。在第 2 步，当东区 pod-1 正在更新"
                    "（容量减半）时，如果 order-svc 东区 pod-2 同时进入 GC 停顿（降级状态），"
                    "关键链路 gateway→order-svc→inventory-svc 有效吞吐量降至 50%，"
                    "低于 66% 的 AvailabilityFloor。"
                ),
                "agent_action": "rolling_update(service=inventory-svc, strategy=one-at-a-time)",
                "sre_context": "大促前一天，发现 inventory-svc 库存扣减有并发 bug，需要紧急滚动更新。当前状态：4 副本（东2西2），已为大促扩容。风险：上游 order-svc 可能因 GC 停顿短暂降级。",
                "key_question": "在最坏情况（滚动更新 + 上游 GC 停顿同时发生）下，链路吞吐量能否保持在 66% 安全阈值以上？",
                "guarantee": "❌ 不能保证。复合故障场景下链路吞吐量降至 50%，低于 66% 安全线。单独的滚动更新是安全的，但叠加 GC 风险就不安全。",
            },
            2: {
                "title": "调整方案：先扩容再更新",
                "description": (
                    "Agent 调整方案：先将 inventory-svc 扩容至 6 副本（东 3 西 3），"
                    "再执行滚动更新。6 副本下，即使更新 + GC 停顿复合场景，"
                    "有效吞吐量仍保持在 66% — 恰好在安全边界。"
                    "BMC 验证 3 步内所有可达状态均通过。"
                ),
                "agent_action": "scale_up(inventory-svc, to=6) && rolling_update(inventory-svc)",
                "sre_context": "团队调整方案：先将 inventory-svc 扩容至 6 副本，再执行滚动更新。6 副本情况下，即使 1 个在更新 + 1 个上游 GC 停顿，仍有 4 个健康副本维持足够容量。",
                "key_question": "扩容至 6 副本后，滚动更新在复合故障下能否维持 66% 安全阈值？",
                "guarantee": "✅ 可以保证。6 副本下复合故障场景有效容量为 66.7%，高于 66% 阈值。",
            },
        },
        "violations": {
            "AvailabilityFloor": (
                "滚动更新第 2 步期间，东区 pod-1 部署中（东区容量 50%）"
                "且 order-svc 东区 pod-2 GC 停顿（降级），"
                "关键链路 gateway→order-svc→inventory-svc 有效吞吐量降至 50%，"
                "低于 66% 的 AvailabilityFloor。"
            ),
        },
        "trace": {
            1: "初始：inventory-svc 4 副本（2E/2W），全部运行。链路吞吐量 = 100%",
            2: "步骤 1：对 inventory-svc east-pod-1 执行滚动更新 → 东区容量 = 1 运行 + 1 部署中（50%）→ 链路吞吐量 = 75%",
            3: "步骤 2：order-svc east-pod-2 进入 GC 停顿（降级）→ order-svc 东区有效 = 66% → 组合链路吞吐量 = 75% × 66% ≈ 50% < 66% AvailabilityFloor ✗",
        },
        "counterexample": {
            1: "状态：{inventory-svc: 2E/2W 运行, order-svc: 3E/3W 运行} — 吞吐量=100%",
            2: "操作：rolling_update(inventory-svc, east-pod-1) → {inventory-svc 东区: 1 运行 + 1 部署中} — 吞吐量=75%",
            3: "环境：order-svc east-pod-2 GC 停顿 → {order-svc 东区: 2 运行 + 1 降级} — 链路吞吐量=50% < 66% ✗ 违反",
        },
        "tla_spec": (
            "--------------------------- MODULE BMCChangeVerification ---------------------------\n"
            "EXTENDS Integers, FiniteSets\n"
            "CONSTANTS Services, Regions, MinSafeReplicas\n"
            "VARIABLES serviceState, replicaCount, deployingSet\n\n"
            "vars == <<serviceState, replicaCount, deployingSet>>\n\n"
            "EffectiveCapacity(s, r) ==\n"
            "    LET total == replicaCount[s][r]\n"
            "        deploying == IF <<s, r>> \\in deployingSet THEN 1 ELSE 0\n"
            "        degraded  == IF serviceState[s][r] = \"gc_pause\" THEN 1 ELSE 0\n"
            "    IN  total - deploying - (degraded \\div 2)\n\n"
            "ChainThroughput(chain) ==\n"
            "    \\* Minimum effective capacity across the chain\n"
            "    LET caps == {EffectiveCapacity(s, \"east\") : s \\in chain}\n"
            "    IN  CHOOSE c \\in caps : \\A c2 \\in caps : c <= c2\n\n"
            "RollingUpdate(s, r) ==\n"
            "    /\\ replicaCount[s][r] >= 2\n"
            "    /\\ deployingSet' = deployingSet \\cup {<<s, r>>}\n"
            "    /\\ UNCHANGED <<serviceState, replicaCount>>\n\n"
            "GCPause(s, r) ==\n"
            "    /\\ serviceState' = [serviceState EXCEPT ![s][r] = \"gc_pause\"]\n"
            "    /\\ UNCHANGED <<replicaCount, deployingSet>>\n\n"
            "AvailabilityFloor ==\n"
            "    \\A s \\in Services :\n"
            "        EffectiveCapacity(s, \"east\") * 3 >= replicaCount[s][\"east\"] * 2\n\n"
            "\\* BMC checks: within 3 steps, is there a reachable state violating AvailabilityFloor?\n"
            "=============================================================================\n"
        ),
    },

    # ── 场景 4 ──────────────────────────────────────────────────────────
    "scenario-4": {
        "phase": "③ 运行时保证",
        "title": "故障拦截——Failover 脑裂",
        "subtitle": "数据库故障转移中的脑裂预防",
        "description": (
            "大促当天峰值期间，东区数据库主节点出现延迟抖动（50% 请求超时）。"
            "场景二合成的控制器触发故障转移。Agent 生成两步计划：先切流量到西区，"
            "再切写入到西区。BMC 检测到此顺序存在脑裂风险。"
        ),
        "constraints": [
            {
                "name": "TrafficWriteConsistency",
                "expression": "activeRegion = dbWriteRegion",
                "threshold": "必须一致",
                "description": "流量区域和写入区域必须相同以防止脑裂",
            },
            {
                "name": "NoSplitBrain",
                "expression": "dbWriteRegion \\in Regions",
                "threshold": "单区域",
                "description": "数据库写入必须来自且仅来自一个区域",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Regions", "activeRegion", "dbWriteRegion", "SwitchTraffic", "SwitchDBWrites"],
                "relevant_section": "多区域故障转移状态机，流量切换与写入切换分别建模",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "NoSplitBrain"],
                "relevant_section": "TrafficWriteConsistency 捕获流量和写入在不同区域的脑裂窗口",
            },
        },
        "steps": {
            1: {
                "title": "Agent 计划：先切流量",
                "description": (
                    "Agent 生成故障转移计划：步骤 A — SwitchTraffic(west)，"
                    "步骤 B — SwitchDBWrites(west)。BMC 检查此两步计划所有可达状态。"
                    "步骤 A 完成后、步骤 B 执行前，activeRegion=west 但 dbWriteRegion=east。"
                    "西区 pay-svc 接收流量并尝试写入，但写入路由到东区数据库（仍是写主节点）。"
                    "同时东区数据库正在恢复，可能接受部分写入，造成脑裂窗口。"
                ),
                "agent_action": "failover_plan: [SwitchTraffic(west), SwitchDBWrites(west)]",
                "sre_context": '大促进行中，东区 MySQL 主库故障。Agent 计划执行故障切换：先切流量到西区，再提升西区 DB 为主库。这是标准的\u201c流量优先\u201d切换流程。',
                "key_question": '\u201c流量优先\u201d切换顺序能否保证不出现脑裂（没有两个 AZ 同时接受写入的窗口）？',
                "guarantee": "❌ 不能保证。存在一个 2 步窗口：流量已切到西区（西区 DB 接收写入），但东区 DB 仍是主库且仍在接受残留东区连接的写入。这产生了脑裂窗口。",
            },
            2: {
                "title": "修正计划：先切写入",
                "description": (
                    "Agent 反转顺序：步骤 A — SwitchDBWrites(west)，"
                    "步骤 B — SwitchTraffic(west)。BMC 验证：步骤 A 后，"
                    "dbWriteRegion=west，activeRegion=east — 流量仍在东区，"
                    "写入转发到西区（安全，只是稍慢）。步骤 B 后，两个区域对齐。"
                    "不存在脑裂窗口。"
                ),
                "agent_action": "failover_plan: [SwitchDBWrites(west), SwitchTraffic(west)]",
                "sre_context": "团队调整顺序：先切 DB 写入到西区（提升西区 DB 为主库），再切流量。这样消除了脑裂窗口，因为写入在流量切换之前就已经统一。",
                "key_question": '\u201c写入优先\u201d切换顺序能否保证不出现脑裂？',
                "guarantee": "✅ 可以保证。先切写入后，不存在两个 DB 同时接受写入的时刻。流量切换只是重定向读请求，直到 DB 提升完成。",
            },
        },
        "violations": {
            "TrafficWriteConsistency": (
                "SwitchTraffic(west) 之后、SwitchDBWrites(west) 之前，"
                "activeRegion=west ≠ dbWriteRegion=east。"
                "流量到达西区服务后尝试写入东区数据库。"
                "存在约 30 秒窗口期两个区域同时接受写入，导致数据不一致。"
            ),
        },
        "trace": {
            1: "初始：activeRegion=east, dbWriteRegion=east, 东区数据库延迟抖动",
            2: "操作：SwitchTraffic(west) → activeRegion=west, dbWriteRegion=east — 不匹配",
            3: "窗口：西区 pay-svc 收到订单 → 写入路由到东区 DB（慢/失败）→ 超时 → 重试可能命中西区 DB 副本 → 脑裂",
        },
        "counterexample": {
            1: "状态：{activeRegion: east, dbWriteRegion: east} — 一致 ✓",
            2: "操作：SwitchTraffic(west) → {activeRegion: west, dbWriteRegion: east} — TrafficWriteConsistency 违反 ✗",
            3: "后果：西区 pay-svc 写入东区 DB（300ms 延迟 + 50% 超时），东区 DB 恢复中仍可接受本地写入",
        },
        "tla_spec": (
            "--------------------------- MODULE FailoverSplitBrain ---------------------------\n"
            "EXTENDS Integers, FiniteSets\n"
            "CONSTANTS Regions\n"
            "VARIABLES activeRegion, dbWriteRegion, dbHealth\n\n"
            "vars == <<activeRegion, dbWriteRegion, dbHealth>>\n\n"
            "TypeOK ==\n"
            "    /\\ activeRegion \\in Regions\n"
            "    /\\ dbWriteRegion \\in Regions\n"
            "    /\\ dbHealth \\in [Regions -> {\"healthy\", \"degraded\", \"down\"}]\n\n"
            "Init ==\n"
            "    /\\ activeRegion = \"east\"\n"
            "    /\\ dbWriteRegion = \"east\"\n"
            "    /\\ dbHealth = [r \\in Regions |-> \"healthy\"]\n\n"
            "SwitchTraffic(r) ==\n"
            "    /\\ activeRegion' = r\n"
            "    /\\ UNCHANGED <<dbWriteRegion, dbHealth>>\n\n"
            "SwitchDBWrites(r) ==\n"
            "    /\\ dbWriteRegion' = r\n"
            "    /\\ UNCHANGED <<activeRegion, dbHealth>>\n\n"
            "DBDegraded(r) ==\n"
            "    /\\ dbHealth' = [dbHealth EXCEPT ![r] = \"degraded\"]\n"
            "    /\\ UNCHANGED <<activeRegion, dbWriteRegion>>\n\n"
            "\\* Key safety properties\n"
            "NoSplitBrain ==\n"
            "    dbWriteRegion \\in Regions  \\* never \"both\"\n\n"
            "TrafficWriteConsistency ==\n"
            "    activeRegion = dbWriteRegion\n\n"
            "\\* BMC finds: SwitchTraffic(west) then SwitchDBWrites(west)\n"
            "\\* creates intermediate state violating TrafficWriteConsistency.\n"
            "\\* Safe sequence: SwitchDBWrites first, then SwitchTraffic.\n"
            "=============================================================================\n"
        ),
    },

    # ── 场景 5 ──────────────────────────────────────────────────────────
    "scenario-5": {
        "phase": "④ 事后复盘 → ①",
        "title": "故障回溯与闭环",
        "subtitle": "从事故分析到规约演进",
        "description": (
            "大促期间实际发生了一次级联故障：运营配置促销弹窗导致 user-svc 查询量 10 倍突增，"
            "Redis 缓存热 key 被驱逐，user-svc 全量回源数据库，连接池耗尽，全链路 5xx。"
            "BMC 逆向分析追踪最短故障路径，生成新规约反馈回阶段一。"
        ),
        "constraints": [
            {
                "name": "CacheHitRateFloor",
                "expression": "\\A s \\in CachedServices : cacheHitRate[s] >= 50",
                "threshold": "50%",
                "description": "缓存依赖服务必须维持最低 50% 命中率",
            },
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]",
                "threshold": "66%",
                "description": "关键路径服务必须维持至少 66% 有效吞吐量",
            },
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "按服务配置",
                "description": "每个关键服务维持最小安全副本数",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "CachedServices", "cacheHitRate", "RedisCacheBurst", "RateLimitService"],
                "relevant_section": "扩展系统模型，新增缓存健康度状态与缓存驱逐故障模式",
            },
            "Properties.tla": {
                "defines": ["CacheHitRateFloor", "AvailabilityFloor", "MinimumRedundancy"],
                "relevant_section": "新增 CacheHitRateFloor 不变量，在缓存降级早期阶段捕获故障",
            },
        },
        "steps": {
            1: {
                "title": "BMC 逆向：追踪故障路径",
                "description": (
                    "从故障终态（全链路 5xx）出发，BMC 逆向搜索到达此状态的最短路径。"
                    "结果：仅需 3 步 — (1) Redis 热 key 驱逐导致缓存命中率降至 12%，"
                    "(2) user-svc 全量回源数据库，耗尽连接池，"
                    "(3) 数据库不可用导致 order-svc 和 pay-svc 失败，触发全链路 5xx。"
                    "根因：现有的 invariant 中没有缓存健康度相关的约束。"
                ),
                "agent_action": "bmc_reverse(terminal_state=full_chain_5xx, max_depth=5)",
                "sre_context": "大促结束后复盘发现一次级联故障：user-svc 的 Redis 缓存发生驱逐风暴，缓存命中率从 99% 骤降至 12%。缓存穿透洪峰压垮数据库，沿服务链级联蔓延。",
                "key_question": "从 Redis 内存压力到全链路级联故障，完整的状态转移路径是什么？",
                "guarantee": "❌ 系统缺少缓存健康不变量。故障路径：Redis 内存压力 → 缓存驱逐 → 命中率降至 12% → 缓存穿透风暴 → DB 过载 → user-svc 超时 → order-svc 队列积压 → 全链路故障。",
            },
            2: {
                "title": "生成新 Invariant",
                "description": (
                    "基于故障路径分析，提出新的安全不变量：CacheHitRateFloor — "
                    "所有缓存依赖服务必须维持至少 50% 缓存命中率。"
                    "同时将新故障模式（CacheBurstEviction）和新防御操作（RateLimitService）"
                    "加入系统模型。BMC 验证：如果 CacheHitRateFloor 存在，"
                    "3 步故障路径在第 1 步（缓存命中率降至 12% < 50%）就会被捕获。"
                ),
                "agent_action": "propose_invariant(CacheHitRateFloor: cacheHitRate >= 50%)",
                "sre_context": "基于故障路径分析，团队定义新的安全不变量：CacheHitRateFloor——缓存服务的命中率必须保持在 50% 以上。一旦突破，系统触发限流以在级联开始前阻断故障传播。",
                "key_question": "新增 CacheHitRateFloor + 限流响应能否阻断已识别的级联故障路径？",
                "guarantee": "✅ 可以保证。当缓存命中率降至 50% 以下时，限流在 DB 过载阈值之前激活，打断级联链条。",
            },
            3: {
                "title": "反馈阶段① — 重新检查可实现性",
                "description": (
                    "将扩展后的规约集（场景一的原始规约 + CacheHitRateFloor + "
                    "CacheBurstEviction 故障模式）进行可实现性检查。"
                    "结果：REALIZABLE。新规约集可以同时满足。"
                    "场景二的控制器可以重新合成，将缓存健康度作为扩缩容决策的前置检查条件。"
                    "闭环完成。"
                ),
                "agent_action": "realizability_check(specs=[relaxed_SLOs, CacheHitRateFloor, CacheBurstEviction])",
                "sre_context": "将新的 CacheHitRateFloor 不变量回馈到阶段 ①。团队需要验证新增约束是否与现有 SLO 冲突——限流可能影响可用性。",
                "key_question": "扩展后的规约集（原始 SLO + CacheHitRateFloor + 限流）是否仍然可同时满足？",
                "guarantee": "✅ 可以保证。限流仅在命中率低于 50% 时激活（异常状态），正常运行下所有 SLO 仍可满足。闭环完成。",
            },
        },
        "violations": {
            "CacheHitRateFloor": (
                "Redis 热 key 驱逐导致缓存命中率降至 12%，远低于 50% 下限。"
                "没有此不变量，监控系统无法在级联到达数据库层之前触发防御措施"
                "（限流、缓存扩容）。"
            ),
        },
        "trace": {
            1: "初始：所有服务运行中，redis cache_hit_rate=99%，数据库连接=20% 使用",
            2: "事件：促销弹窗 → user-svc 查询量 10x → redis 热 key 驱逐 → cache_hit_rate 降至 12%",
            3: "级联：user-svc 缓存未命中 → 全量查询数据库 → 连接池=100% → 数据库超时",
            4: "终态：数据库不可用 → order-svc 失败 → pay-svc 失败 → gateway 所有请求返回 5xx",
        },
        "counterexample": {
            1: "状态：{redis: cache_hit_rate=99%, database: connections=20%, 所有服务: 运行中} — 健康",
            2: "操作：RedisCacheBurst(user-svc) → {redis: cache_hit_rate=12%} — CacheHitRateFloor 违反（如果不变量存在）",
            3: "级联：database connections=100% → 超时 → {order-svc: 不可用, pay-svc: 不可用} → 全链路 5xx",
            4: "有 CacheHitRateFloor：步骤 2 捕获违反 → 触发 RateLimitService(user-svc) + ScaleUp(redis) → 级联被阻止",
        },
        "tla_spec": (
            "--------------------------- MODULE FeedbackLoop ---------------------------\n"
            "EXTENDS Integers, FiniteSets\n"
            "CONSTANTS Services, CachedServices, MinCacheHitRate\n"
            "VARIABLES cacheHitRate, dbConnections, serviceStatus, queryMultiplier\n\n"
            "vars == <<cacheHitRate, dbConnections, serviceStatus, queryMultiplier>>\n\n"
            "TypeOK ==\n"
            "    /\\ cacheHitRate \\in [CachedServices -> 0..100]\n"
            "    /\\ dbConnections \\in 0..100\n"
            "    /\\ serviceStatus \\in [Services -> {\"running\", \"degraded\", \"down\"}]\n"
            "    /\\ queryMultiplier \\in 1..20\n\n"
            "Init ==\n"
            "    /\\ cacheHitRate = [s \\in CachedServices |-> 99]\n"
            "    /\\ dbConnections = 20\n"
            "    /\\ serviceStatus = [s \\in Services |-> \"running\"]\n"
            "    /\\ queryMultiplier = 1\n\n"
            "RedisCacheBurst(s) ==\n"
            "    /\\ s \\in CachedServices\n"
            "    /\\ queryMultiplier' = queryMultiplier * 10\n"
            "    /\\ cacheHitRate' = [cacheHitRate EXCEPT ![s] = 12]\n"
            "    /\\ dbConnections' = IF dbConnections + 80 > 100 THEN 100 ELSE dbConnections + 80\n"
            "    /\\ UNCHANGED serviceStatus\n\n"
            "DBOverload ==\n"
            "    /\\ dbConnections = 100\n"
            "    /\\ serviceStatus' = [s \\in Services |-> \"down\"]\n"
            "    /\\ UNCHANGED <<cacheHitRate, dbConnections, queryMultiplier>>\n\n"
            "\\* New invariant proposed from post-incident analysis\n"
            "CacheHitRateFloor ==\n"
            "    \\A s \\in CachedServices : cacheHitRate[s] >= MinCacheHitRate\n\n"
            "\\* BMC reverse trace: from terminal state (all down),\n"
            "\\* shortest path is 3 steps: CacheBurst -> DBOverload -> AllDown\n"
            "\\* With CacheHitRateFloor, step 1 is caught immediately.\n"
            "=============================================================================\n"
        ),
    },
}
