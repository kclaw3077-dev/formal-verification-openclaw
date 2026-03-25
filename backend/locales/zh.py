"""Chinese locale — all user-facing scenario text."""

SCENARIOS = {
    # ── 场景 1 ──────────────────────────────────────────────────────────
    "scenario-1": {
        "title": "场景一：滚动更新中的隐式容量瓶颈",
        "subtitle": "一次看似安全的更新触发了隐藏的吞吐量危机",
        "description": (
            "Agent 收到指令：对 order-svc 进行滚动更新（v1→v2）。"
            "更新过程每次只下线 1 个副本（保持 2/3 可用），看起来很安全。"
            "但 order-svc 依赖的 inventory-svc 在东区只有 2 个副本，"
            "且其中一个正处于 GC 停顿状态。TLA+ 模型检查器探索了完整请求链路，"
            "发现有效吞吐量降到了安全阈值以下。"
        ),
        "constraints": [
            {
                "name": "AvailabilityFloor",
                "expression": "\\A s \\in CriticalPath : EffectiveCapacity(s) >= 66%",
                "threshold": "66%",
                "description": "关键请求路径上的有效容量必须保持在 66% 以上",
            },
            {
                "name": "MinSafeReplicas",
                "expression": "TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "order-svc: 2, inventory-svc: 2",
                "description": "滚动更新始终保持至少 2/3 的副本在运行",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "Regions", "serviceState", "RollingUpdate", "ReplicaFailure", "EffectiveCapacity"],
                "relevant_section": "建模服务状态转换与滚动更新对有效容量的影响",
            },
            "Properties.tla": {
                "defines": ["AvailabilityFloor", "MinimumRedundancy", "NoSimultaneousUpdatesOnChain"],
                "relevant_section": "AvailabilityFloor 不变量捕获了链路吞吐量降至 66% 安全下限以下",
            },
        },
        "steps": {
            1: {
                "title": "背景：inventory-svc GC 停顿",
                "description": (
                    "inventory-svc 东区第 2 个副本进入长时间 GC 停顿，"
                    "有效容量降至 1/2。"
                    "由于这是环境事件（非 Agent 操作），"
                    "验证门禁仅执行基础健康监控："
                    "副本数仍为 2（Pod 在运行，只是变慢），"
                    "MinimumRedundancy 通过。"
                    "AvailabilityFloor（链路吞吐量分析）仅在 Agent 提出变更时触发。"
                ),
                "agent_action": "[环境事件] 检测到 inventory-svc GC 停顿",
            },
            2: {
                "title": "Agent 操作：滚动更新 order-svc",
                "description": (
                    "Agent 提议：对 order-svc 东区执行滚动更新（v1→v2）。"
                    "更新期间，3 个 order-svc 副本中有 1 个正在被替换，"
                    "因此 order-svc 有效容量 = 2.5/3。"
                    "但 order-svc 依赖的 inventory-svc 已经只有 1/2 的容量。"
                    "链路综合容量：min(2.5/3, 1/2) = 50% —— 低于 66% 的安全下限。"
                ),
                "agent_action": "rolling_update(order-svc, east, v1→v2)",
            },
        },
        "violations": {
            "AvailabilityFloor": (
                "关键路径上的有效容量降至安全阈值以下。"
                "order-svc（部署中）→ inventory-svc（降级）："
                "链路吞吐量 = min(83%, 50%) = 50%，低于 66% 的安全下限。"
            ),
        },
        "trace": {
            1: "初始状态：所有服务正常运行",
            2: "inventory-svc 东区副本进入 GC 停顿",
            3: "Agent 启动 order-svc 东区滚动更新",
        },
        "counterexample": {
            1: "初始：全部健康",
            2: "ReplicaFailure(inventory-svc, east)",
            3: "RollingUpdate(order-svc, east)",
        },
        "tla_spec": (
            "\\* 被违反的关键不变量：\n"
            "AvailabilityFloor ==\n"
            "    \\A s \\in CriticalPath :\n"
            "        EffectiveCapacity(s) * 2 >= MinSafeReplicas[s]\n\n"
            "\\* 模型检查器探索了以下状态：\n"
            "\\* - inventory-svc 处于降级状态（GC 停顿）\n"
            "\\* - order-svc 进入部署状态\n"
            "\\* 链路综合容量降至阈值以下。"
        ),
    },

    # ── 场景 2 ──────────────────────────────────────────────────────────
    "scenario-2": {
        "title": "场景二：隐蔽的循环依赖",
        "subtitle": "一个退款功能引入了不可见的死锁风险",
        "description": (
            "Agent 收到指令：在 pay-svc 的退款流程中添加订单状态校验"
            "（pay-svc 需要调用 order-svc）。当前依赖：order-svc → pay-svc（用于支付）。"
            "新增后变成 order-svc ⇄ pay-svc 双向依赖。"
            "这个循环仅在退款路径上触发，正常支付流程中完全不可见。"
            "TLA+ 传递闭包分析瞬间捕获了这个循环。"
        ),
        "constraints": [
            {
                "name": "NoCyclicDependencies",
                "expression": "\\A s \\in Services : s \\notin ReachableFrom(s, {}, deps)",
                "threshold": "0 个循环",
                "description": "服务依赖图必须是有向无环图（DAG）——不允许循环依赖",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "dependencies", "AddDependency", "ReachableFrom"],
                "relevant_section": "建模依赖图和传递闭包计算，用于循环检测",
            },
            "Properties.tla": {
                "defines": ["NoCyclicDependencies", "HasCycle"],
                "relevant_section": "NoCyclicDependencies 不变量通过传递闭包检测依赖图中的任何循环",
            },
        },
        "steps": {
            1: {
                "title": "Agent 操作：添加退款校验依赖",
                "description": (
                    "产品团队要求：在处理退款前，pay-svc 应该调用 order-svc "
                    "来验证订单状态。这看起来是合理的业务需求。"
                    "Agent 提议添加这条依赖。"
                ),
                "agent_action": "add_dependency(pay-svc → order-svc, purpose='refund_verification')",
            },
            2: {
                "title": "TLA+ 建议：打破循环",
                "description": (
                    "验证器不仅捕获了循环，模型还表明另一种设计——"
                    "使用异步事件总线代替同步调用——可以消除循环依赖。"
                    "pay-svc 发布 'refund_requested' 事件，"
                    "由独立的对账服务检查订单状态。"
                ),
                "agent_action": "[建议] 使用事件驱动模式避免同步循环",
            },
        },
        "violations": {
            "NoCyclicDependencies": (
                "检测到循环依赖："
                "order-svc → pay-svc → order-svc。"
                "此循环会产生死锁风险：如果 order-svc 响应慢，"
                "pay-svc 退款调用阻塞，进而阻塞 order-svc 的支付回调，"
                "形成级联超时螺旋。"
            ),
        },
        "trace": {
            1: "当前：order-svc 依赖 pay-svc",
            2: "提议：pay-svc 添加对 order-svc 的依赖",
            3: "发现循环：order-svc → pay-svc → order-svc",
        },
        "counterexample": {
            1: "初始：DAG 无环",
            2: "AddDependency(pay-svc, order-svc)",
        },
        "tla_spec": (
            "\\* 通过传递闭包检测循环：\n"
            "RECURSIVE ReachableFrom(_,_,_)\n"
            "ReachableFrom(s, visited, deps) ==\n"
            "    LET directDeps == deps[s] \\\\ visited\n"
            "    IN  directDeps \\cup\n"
            "        UNION {ReachableFrom(d, visited \\cup directDeps, deps) : d \\in directDeps}\n\n"
            "HasCycle(deps) ==\n"
            "    \\E s \\in Services : s \\in ReachableFrom(s, {}, deps)\n\n"
            "NoCyclicDependencies == ~HasCycle(dependencies)"
        ),
    },

    # ── 场景 3 ──────────────────────────────────────────────────────────
    "scenario-3": {
        "title": "场景三：Failover 中的脑裂",
        "subtitle": "三步切换计划存在竞态条件窗口",
        "description": (
            "Agent 收到指令：将流量从东区切换到西区。"
            "Agent 的计划：(1) 切换 DNS 到西区，(2) 等待 30 秒连接排空，"
            "(3) 切换数据库写入到西区。TLA+ 发现在步骤 1 和步骤 3 之间，"
            "流量已切到西区但数据库写入仍在东区——西区的读取会看到过期数据。"
            "更严重的是：如果步骤 3 失败（网络分区），系统将永久处于不一致状态。"
        ),
        "constraints": [
            {
                "name": "TrafficWriteConsistency",
                "expression": "activeRegion = dbWriteRegion",
                "threshold": "始终相等",
                "description": "流量服务区域和数据库写入区域必须始终一致，避免读取过期数据",
            },
            {
                "name": "NoSplitBrain",
                "expression": "dbWriteRegion \\in Regions",
                "threshold": "恰好 1 个区域",
                "description": "任何时刻最多只有一个区域可以接受数据库写入——绝不允许同时写入两个区域",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Regions", "activeRegion", "dbWriteRegion", "SwitchTraffic", "SwitchDBWrites"],
                "relevant_section": "建模多区域切换状态机，流量开关和写入开关分别建模",
            },
            "Properties.tla": {
                "defines": ["TrafficWriteConsistency", "NoSplitBrain"],
                "relevant_section": "TrafficWriteConsistency 捕获流量和写入在不同区域的窗口期",
            },
        },
        "steps": {
            1: {
                "title": "Agent 操作：将流量切换到西区",
                "description": (
                    "Agent 执行切换计划的第一步：将 DNS 指向西区。"
                    "新请求现在转到西区。但数据库写入仍在东区。"
                    "西区服务的写入需要跨区域到东区 DB（高延迟），"
                    "且西区副本的读取可能看到过期数据。"
                ),
                "agent_action": "switch_traffic(west)",
            },
            2: {
                "title": "TLA+ 建议：原子性切换协议",
                "description": (
                    "正确的顺序是：(1) 停止东区写入，(2) 等待复制同步，"
                    "(3) 启用西区写入，(4) 切换流量。这确保每个中间状态都满足一致性。"
                    "TLA+ 验证了这个替代方案在每个中间状态都满足 TrafficWriteConsistency。"
                ),
                "agent_action": "[修正方案] stop_writes(east) → sync → enable_writes(west) → switch_traffic(west)",
            },
        },
        "violations": {
            "TrafficWriteConsistency": (
                "将流量切换到西区后，数据库写入仍在东区。"
                "状态：activeRegion=west, dbWriteRegion=east。"
                "这违反了 TrafficWriteConsistency：读取可能返回过期数据。"
                "不一致持续时间取决于步骤 3 何时完成。"
            ),
        },
        "trace": {
            1: "初始：traffic=east, writes=east（一致）",
            2: "SwitchTraffic(west): traffic=west, writes=east",
        },
        "counterexample": {
            1: "初始：activeRegion=east, dbWriteRegion=east",
            2: "SwitchTraffic(west)",
            3: "[网络分区] SwitchDBWrites 失败",
        },
        "tla_spec": (
            "\\* 两个关键属性：\n"
            "NoSplitBrain ==\n"
            "    dbWriteRegion \\in Regions  \\* 永远不能为 \"both\"\n\n"
            "TrafficWriteConsistency ==\n"
            "    activeRegion = dbWriteRegion\n\n"
            "\\* TLC 发现先执行 SwitchTraffic(west) 再执行 SwitchDBWrites(west)\n"
            "\\* 会产生违反 TrafficWriteConsistency 的中间状态。\n"
            "\\* 安全的顺序：先切换写入，再切换流量。"
        ),
    },

    # ── 场景 4 ──────────────────────────────────────────────────────────
    "scenario-4": {
        "title": "场景四：并发操作冲突",
        "subtitle": "两个安全操作组合成一个危险状态",
        "description": (
            "Agent 收到两个独立的运维请求："
            "(A) 给 user-svc 打安全补丁，(B) 扩容数据库副本。"
            "每个操作单独来看都是安全的。但 TLA+ 状态空间探索发现，"
            "两者并发执行时，user-svc 重启后重连数据库，"
            "而此时数据库正在 rebalance。重连风暴 + rebalance 开销"
            "级联导致集群级别的故障。"
        ),
        "constraints": [
            {
                "name": "NoSimultaneousUpdatesOnChain",
                "expression": "\\A s, t on same chain : ~(deploying(s) /\\ deploying(t))",
                "threshold": "每条链路最多 1 个部署中",
                "description": "同一依赖链路上的两个服务不能同时处于部署状态",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "dependencies", "serviceState", "RollingUpdate", "ScaleUp"],
                "relevant_section": "建模滚动更新和扩容的并发执行，作为交错的状态转换",
            },
            "Properties.tla": {
                "defines": ["NoSimultaneousUpdatesOnChain", "AvailabilityFloor"],
                "relevant_section": "NoSimultaneousUpdatesOnChain 检测 user-svc 和 database 同时部署的危险交错",
            },
        },
        "steps": {
            1: {
                "title": "请求 A：user-svc 安全补丁",
                "description": (
                    "安全团队要求：给 user-svc 打 CVE-2024-XXXX 补丁。"
                    "需要滚动重启。单独来看是安全的：3 个副本，"
                    "滚动更新始终保持 2 个运行。"
                ),
                "agent_action": "rolling_update(user-svc, east, security_patch)",
            },
            2: {
                "title": "请求 B：数据库副本扩容",
                "description": (
                    "DBA 团队要求：给东区数据库增加 1 个副本以提升容量。"
                    "单独来看是安全的：添加副本不会影响现有副本。"
                    "但 rebalance 期间，现有副本延迟会升高。"
                ),
                "agent_action": "scale_up(database, east, 1) + rebalance",
            },
            3: {
                "title": "组合：两个操作并发执行",
                "description": (
                    "当两个操作同时执行时，TLA+ 发现了一个危险的交错序列："
                    "(1) user-svc 副本重启，(2) 重连数据库，"
                    "(3) 数据库正在 rebalance → 连接被拒绝，"
                    "(4) user-svc 重试风暴压垮数据库，"
                    "(5) 其他服务的数据库连接也被拒绝。"
                    "这种组合爆炸是人工推理极易遗漏的。"
                ),
                "agent_action": "[并发] rolling_update(user-svc) + scale_up(database)",
            },
        },
        "violations": {
            "NoSimultaneousUpdatesOnChain": (
                "user-svc 和 database 在同一依赖链上"
                "（user-svc → database）。两者同时进入部署状态"
                "违反了 NoSimultaneousUpdatesOnChain 属性。"
                "在重叠窗口期，user-svc 重连风暴 + "
                "数据库 rebalance 会产生级联故障。"
            ),
        },
        "trace": {
            1: "初始：所有服务正常运行",
            2: "RollingUpdate(user-svc, east)",
            3: "ScaleUp(database, east, 1) 触发 rebalance",
        },
        "counterexample": {
            1: "初始：全部运行中",
            2: "RollingUpdate(user-svc, east)",
            3: "ScaleUp(database, east, 1) + rebalance",
        },
        "tla_spec": (
            "\\* 关键属性：同一链路上的两个服务不能同时更新\n"
            "NoSimultaneousUpdatesOnChain ==\n"
            "    \\A s \\in Services : \\A t \\in dependencies[s] :\n"
            "        ~(\\E r1, r2 \\in Regions :\n"
            "            serviceState[s][r1] = \"deploying\" /\\ serviceState[t][r2] = \"deploying\")\n\n"
            "\\* TLC 探索了 8,923 个状态，找到了\n"
            "\\* user-svc 和 database 同时处于部署状态的交错序列。\n"
            "\\* 每个操作单独安全，组合后不安全。"
        ),
    },

    # ── 场景 5 ──────────────────────────────────────────────────────────
    "scenario-5": {
        "title": "场景五：缩容的级联效应",
        "subtitle": "成本优化引入了单点故障",
        "description": (
            "Agent 观测到凌晨 3 点流量低谷，提议：将 inventory-svc 东区"
            "从 2 个副本缩容到 1 个以节约成本。看起来合理——流量只有峰值的 20%。"
            "但 TLA+ 穷举检查了缩容后的所有状态（包括故障场景）："
            "如果唯一剩余的副本发生故障，order-svc 和 pay-svc 都将失去库存服务能力。"
            "关键路径可用性从 99.9% 降至 0%。"
            "恢复时间（拉起新副本 + 数据预热）超过 SLA 允许的最大中断时间。"
        ),
        "constraints": [
            {
                "name": "MinimumRedundancy",
                "expression": "\\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]",
                "threshold": "inventory-svc: \u2265 2",
                "description": "关键路径服务即使在变更后的故障场景中也必须维持最低副本数",
            },
            {
                "name": "SLA Compliance",
                "expression": "RecoveryTime(s) <= MaxDowntime",
                "threshold": "恢复 < 5 分钟",
                "description": "任何单点故障的恢复时间必须在 SLA 最大中断窗口内",
            },
        ],
        "spec_refs": {
            "SREInfrastructure.tla": {
                "defines": ["Services", "CriticalPath", "TotalReplicas", "ScaleDown", "ReplicaFailure"],
                "relevant_section": "建模缩容后副本故障的场景，探索所有变更后的可达状态",
            },
            "Properties.tla": {
                "defines": ["MinimumRedundancy", "AvailabilityFloor", "NoCyclicDependencies"],
                "relevant_section": "MinimumRedundancy 不变量通过找到 TotalReplicas = 0 的可达状态证明操作不安全",
            },
        },
        "steps": {
            1: {
                "title": "Agent 提议：成本优化缩容",
                "description": (
                    "凌晨 3 点，流量为峰值的 20%。Agent 的成本优化模块建议："
                    "将 inventory-svc 东区从 2→1 个副本，每月节省 $47。"
                    "当前负载 1 个副本即可承载，还有 60% 的余量。"
                ),
                "agent_action": "scale_down(inventory-svc, east, 1)  # 低流量时节约成本",
            },
            2: {
                "title": "形式化保证：不降级原则",
                "description": (
                    "用 TLA+ 形式化的不降级原则："
                    "对于操作后的所有可达状态（包括故障状态），"
                    "可用性不得降低。这比仅检查操作后的即时状态更强——"
                    "它检查每一个可能的未来。"
                    "每月省 $47 不值得冒违反 SLA 的风险。"
                ),
                "agent_action": "[已拦截] 操作被验证门禁拒绝",
            },
        },
        "violations": {
            "MinimumRedundancy": (
                "缩容至 1 个副本后，inventory-svc 东区没有冗余。"
                "TLA+ 探索了后继状态——该唯一副本故障的情况："
                "TotalReplicas(inventory-svc) 在东区 = 0，低于 "
                "MinSafeReplicas[inventory-svc] = 2。"
                "这在关键路径上引入了单点故障"
                "（gateway → order-svc → inventory-svc）。"
            ),
        },
        "trace": {
            1: "初始：inventory-svc 东区 = 2 个副本",
            2: "ScaleDown(inventory-svc, east, 1)",
            3: "ReplicaFailure(inventory-svc, east) —— 单点故障",
            4: "级联：order-svc 无法访问 inventory-svc",
        },
        "counterexample": {
            1: "初始：inventory-svc.east=running(2)",
            2: "ScaleDown(inventory-svc, east, 1)",
            3: "ReplicaFailure(inventory-svc, east)",
        },
        "tla_spec": (
            "\\* 不降级原则：最低冗余必须在所有可达状态中成立\n"
            "\\* 包括变更后的故障场景。\n"
            "MinimumRedundancy ==\n"
            "    \\A s \\in CriticalPath : TotalReplicas(s) >= MinSafeReplicas[s]\n\n"
            "\\* TLC 在所有可达状态上检查此不变量。\n"
            "\\* ScaleDown(inventory-svc, east, 1) 之后，TLC 探索：\n"
            "\\*   ScaleDown → ReplicaFailure → TotalReplicas = 0 < 2 = MinSafe\n"
            "\\* 不变量违反证明了该操作不安全\n"
            "\\* 即使操作后的即时状态看起来没问题。"
        ),
    },
}
