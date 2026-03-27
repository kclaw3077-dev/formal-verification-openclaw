# 形式化方法在 SRE 中的应用

## 1. 核心概念总览

### 1.1 三种方法的关系

```
Model Checking:        ∀env. (M × env) ⊨ φ         验证已有系统是否满足规约
Realizability Check:   ∃M. ∀env. (M × env) ⊨ φ ?   判断规约是否存在可行解
Reactive Synthesis:    ∃M. ∀env. (M × env) ⊨ φ → M  从规约直接合成正确的系统
```

| 方法 | 已知 | 求解 | 类比 |
|------|------|------|------|
| Model Checking | 系统 M + 规约 φ | M ⊨ φ ? | 判卷 |
| Realizability Check | 规约 φ | ∃M. M ⊨ φ ? | 看题目有没有解 |
| Reactive Synthesis | 规约 φ | 找到满足 φ 的 M | 写出标准答案 |

### 1.2 Model Checking

给定一个**已有的系统实现**和一个**规约**，穷举所有可达状态，验证系统是否在所有路径上满足规约。本质是 **verification**——判卷。

- 输入：系统 M（已知）+ 规约 φ
- 输出：Yes / No + 反例路径
- 复杂度瓶颈：状态空间爆炸

### 1.3 Reactive Synthesis

给定**仅有的规约**（通常用 LTL 时序逻辑表达），自动合成一个 reactive system，使其在与任意环境交互时始终满足规约。本质是 **construction**——写卷。

- 输入：仅有规约 φ
- 输出：满足规约的系统 M（有限状态自动机），或报告 UNREALIZABLE
- 核心抽象：无限步二人博弈（环境 vs 系统），求系统的必胜策略
- 关键约束：因果性（causality）——每步决策只能基于历史输入，不能偷看未来
- 复杂度：2EXPTIME-complete（LTL 规约下）

### 1.4 Realizability Check

Reactive Synthesis 的判定版本——只回答"有没有解"，不实际构造解。

- 输入：规约 φ
- 输出：REALIZABLE / UNREALIZABLE
- 价值：当系统验证失败时，区分"实现写得不好"和"需求本身不可能满足"

### 1.5 Bounded Model Checking (BMC)

将搜索深度限定在 k 步以内，把无限状态空间的验证问题转化成有限的 SAT/SMT 求解问题。

- 输入：初始状态 + 转移规则 + 故障模式 + 步数上限 k
- 输出：k 步内的具体故障路径，或"k 步内安全"
- 优势：避免状态空间爆炸，适合实际故障链长度（通常 3-7 步）

---

## 2. SRE 应用场景

### 2.1 场景一：Change Management — 验证变更 SOP（Model Checking）

**问题：已有一个变更 SOP，验证它在所有可能的环境条件下是否安全。**

以 Canary Deployment Policy 为例：

```python
# 人写的 rollout policy（已有的 M）
def human_written_policy(state) -> Action:
    if state.error_rate > 0.01:
        return ROLLBACK
    if state.observation_windows_passed >= 3 and state.error_rate < 0.001:
        return SCALE_UP
    return HOLD

# Model Checker 穷举所有可达状态
def model_check(policy, spec) -> bool | Counterexample:
    queue = [INITIAL_STATE]
    visited = set()
    
    while queue:
        state = queue.pop()
        if state in visited:
            continue
        visited.add(state)
        
        for env_input in all_possible_env_inputs(state):
            action = policy(state)
            next_state = transition(state, env_input, action)
            
            if violates_spec(next_state, spec):
                return Counterexample(trace_to(next_state))
            
            queue.append(next_state)
    
    return True
```

典型应用：

- 验证 canary deployment policy 在所有故障场景下是否守住 SLO
- 验证 database migration runbook 在任意步骤失败回滚后数据一致性

### 2.2 场景二：Change Management — 自动合成 Rollout Controller（Reactive Synthesis）

**问题：只给出安全规约，自动生成一个正确的金丝雀发布控制器。**

#### 第一步：定义环境与系统变量

```python
# 环境变量（不可控）
env_vars = {
    "canary_error":   Enum("low", "medium", "high"),
    "baseline_error": Enum("low", "medium", "high"),
    "traffic_surge":  Bool,
    "node_failure":   Bool,
}

# 系统变量（要合成的决策）
sys_vars = {
    "canary_pct":  Enum(0, 1, 5, 25, 50, 100),
    "action":      Enum("PROMOTE", "HOLD", "ROLLBACK"),
}
```

#### 第二步：只写规约

```python
spec = {
    # Safety: 金丝雀 error 显著高于 baseline 时禁止扩量
    "S1": "G( (canary_error==high ∧ baseline_error==low) → action ≠ PROMOTE )",

    # Safety: 每次扩量只能升一档
    "S2": "G( action==PROMOTE → X(canary_pct)==next_stage(canary_pct) )",

    # Safety: 流量突增期间冻结变更（除非 error 已经 high）
    "S3": "G( (traffic_surge ∧ canary_error≠high) → action==HOLD )",

    # Safety: 节点故障时立即回滚
    "S4": "G( node_failure → X(action==ROLLBACK) )",

    # Liveness: 环境持续健康则最终完成发布
    "L1": "G(F(healthy_env)) → F(canary_pct==100)",

    # Reaction: 连续 3 窗口 high error 必须回滚
    "R1": "G( 3_consecutive_high → next(action==ROLLBACK) )",

    # Cooldown: 回滚后至少 5 个窗口才能再次扩量
    "C1": "G( action==ROLLBACK → next_5_steps(action≠PROMOTE) )",
}
```

#### 第三步：Synthesizer 自动生成 Controller

```python
def reactive_synthesize(env_vars, sys_vars, spec):
    # LTL → Deterministic Parity Automaton
    dpa = ltl_to_dpa(spec)
    
    # 构建博弈竞技场
    game = build_game_arena(env_vars, sys_vars, dpa)
    
    # 求解博弈
    winning_region, strategy = solve_parity_game(game)
    
    if game.initial_state not in winning_region:
        return UNREALIZABLE
    
    # 提取状态机
    return extract_mealy_machine(strategy)
```

#### 合成结果：一张状态转移表（不是人写的）

```
State       | Condition                        | Action    | Next Pct | Next State
------------+----------------------------------+-----------+----------+-----------
S_0pct      | low, low, no surge, no failure   | PROMOTE   | 1%       | S_1pct
S_1pct      | low, low, no surge, no failure   | PROMOTE   | 5%       | S_5pct
S_1pct      | high, low, no surge, no failure  | HOLD      | 1%       | S_1pct_high1
S_1pct_high1| high, low, ...                   | HOLD      | 1%       | S_1pct_high2
S_1pct_high2| high, low, ...                   | ROLLBACK  | 0%       | S_cooldown_0
S_50pct     | high, low, ...                   | ROLLBACK  | 0%       | S_cooldown_0
S_cooldown_N| any (N<5)                        | HOLD      | 0%       | S_cooldown_N+1
S_cooldown_4| any                              | HOLD      | 0%       | S_0pct
S_done      | any                              | HOLD      | 100%     | S_done
```

**关键洞察：** Synthesizer 自动发现，在 1% 流量时可以容忍 3 次 high error 再回滚，但在 50% 流量时 1 次 high 就必须立即回滚——因为 50% × high_error 已经逼近 SLO 阈值。这个分界点是数学推导出来的，不是拍脑袋。

#### 运行时：纯查表，O(1)

```python
class CanaryController:
    def __init__(self):
        self.state = "S_0pct"
    
    def tick(self, canary_error, baseline_error, traffic_surge, node_failure):
        key = (self.state, canary_error, baseline_error, traffic_surge, node_failure)
        result = CONTROLLER[key]
        self.state = result.next_state
        return result.action, result.next_pct
```

Synthesis 把复杂度从运行时搬到了编译时：合成过程可能耗时，但输出的 controller 是极轻量的有限状态自动机。

### 2.3 场景三：SOP 验证 + 修复流水线（三种方法组合）

**问题：在严格独立变更假设下，验证一个变更 SOP 是否正确，并在失败时给出修复方案。**

```python
def validate_change_sop(sop, spec, env_model):
    
    # Step 1: Realizability Check — 规约本身有没有解？
    result = realizability_check(spec, env_model)
    if result == UNREALIZABLE:
        return "规约本身有矛盾，需要放松约束"
    
    # Step 2: Model Checking — 你的 SOP 对不对？
    mc_result = model_check(sop, spec, env_model)
    if mc_result.passed:
        return "SOP 正确 ✓"
    
    # Step 3: Reactive Synthesis — 正确答案长什么样？
    optimal = synthesize(spec, env_model)
    
    # Step 4: 对比差异
    diff = compare_strategies(sop, optimal)
    return {
        "verdict":       "SOP 有缺陷",
        "counterexample": mc_result.counterexample,
        "root_cause":     diff.divergence_points,
        "suggested_fix":  optimal,
    }
```

三步分别回答了：

| 步骤 | 方法 | 回答的问题 |
|------|------|-----------|
| Step 1 | Realizability Check | 这道题有没有解？ |
| Step 2 | Model Checking | 你的答案对不对？ |
| Step 3 | Reactive Synthesis | 标准答案是什么？ |

### 2.4 场景四：故障模式路径验证（Bounded Model Checking）

**问题：在给定的生产环境配置下，是否存在 ≤k 步的事件序列能触发某个已知故障模式？**

与 Change Management 形成对偶关系：

```
Change Management:     ∃strategy. ∀env. 路径 ⊨ "成功"    建设性：怎么做能成功
Fault Path Verification: ∃env_trace. 路径 ⊨ "故障模式"    破坏性：怎么会出事
```

#### 具体场景：Inference Serving Cluster 的 Cascading Failure 检测

系统架构：

```
用户请求 → [Gateway 10pods] → [Inference 5pods] → [Model Store (S3)]
                  ↓
           [Redis Cache 90% hit rate]
```

#### 定义系统状态

```python
state = {
    "rps":                  500,
    "cache_hit_rate":       0.9,
    "inference_pods":       5,
    "model_store_conns":    5,     # 连接池上限 50
    "inference_cpu_pct":    40,
    "global_error_rate":    0.001,
    "retry_multiplier":     1.0,
}
```

#### 定义转移规则（从 Postmortem 提炼）

```python
rules = [
    # cache 命中率下降 → 更多请求穿透到 model store
    "model_store_conns' = rps * (1 - cache_hit_rate)",

    # 连接池满 → 请求全部报错
    "IF model_store_conns >= 50 THEN model_store_error_rate' = 1.0",

    # 下游报错 → gateway 重试 → 流量翻倍
    "IF model_store_error_rate > 0.5 THEN retry_multiplier' = retry_multiplier * 2",

    # 实际流量决定 CPU
    "inference_cpu_pct' = (rps * retry_multiplier) / (inference_pods * 200) * 100",

    # CPU 过高 → pod OOM 被杀
    "IF inference_cpu_pct > 95 THEN inference_pods' = inference_pods - 1",
]
```

#### 定义故障模式（骨牌倒的顺序）

```python
# 核心就是"时序因果链：A 发生在 B 之前，B 发生在 C 之前"

def is_cascading_overload(trace):
    """检查一条状态序列里，三块骨牌是否按顺序倒下"""
    step_cache = None
    step_backend = None
    step_global = None
    
    for i, state in enumerate(trace):
        # 骨牌 1: cache 命中率跌破 50%
        if state.cache_hit_rate < 0.5:
            if step_cache is None:
                step_cache = i
        
        # 骨牌 2: model store 连接池耗尽（且在骨牌1之后）
        if (step_cache is not None and i > step_cache
            and state.model_store_conns >= 50):
            if step_backend is None:
                step_backend = i
        
        # 骨牌 3: 全局 error rate 爆了（且在骨牌2之后）
        if (step_backend is not None and i > step_backend
            and state.global_error_rate > 0.1):
            step_global = i
    
    return step_global is not None
```

其他常见故障模式的骨牌链：

```
cascading_overload: cache 降级 → backend 饱和 → 全局故障
retry_storm:        某服务变慢 → 重试放大 → 继续放大 → 全部过载
thundering_herd:    cache 全失效 → backend 流量 10x → backend 全挂
split_brain:        网络分区 → 双主 → 数据不一致
```

#### BMC 手动模拟（k=5，触发事件：Redis 内存满，命中率跌到 20%）

```
Step 0: cache_hit=0.2 → model_store_conns = 500*0.8 = 400 >> 50
        ✓ 骨牌1: cache_hit < 0.5

Step 1: conns=400 >> 50 → error_rate=1.0 → retry=1*2=2
        实际流量 500*2=1000, cpu=1000/(5*200)*100=100%
        ✓ 骨牌2: conns >= 50

Step 2: cpu=100%>95% → pods=4, retry=2*2=4
        实际流量 500*4=2000, cpu=2000/(4*200)*100=250%

Step 3: pods=3, retry=4*2=8, 流量=4000, cpu=667%
        global_error_rate > 0.1
        ✓ 骨牌3: error > 10%

Step 4: pods→2→1→0, 全崩
```

#### BMC 求解器自动化

```python
def bounded_check(init, rules, fault_pattern, k=5):
    solver = Z3()
    
    # 造 k+1 个快照
    snapshots = [make_symbolic_state(f"s_{i}") for i in range(k + 1)]
    
    # 初始状态约束
    solver.add(encode_init(snapshots[0], init))
    # cache_hit_rate 不钉死——让求解器自己找什么值会出事
    
    # 转移关系连接每一步
    for i in range(k):
        solver.add(encode_transition(snapshots[i], snapshots[i+1], rules))
    
    # 故障模式约束
    solver.add(encode_fault_pattern(snapshots, fault_pattern))
    
    if solver.check() == SAT:
        model = solver.model()
        trace = [extract(model, snapshots[i]) for i in range(k + 1)]
        return Vulnerable(trace)   # 具体的故障复现路径
    else:
        return Safe(depth=k)       # k 步内不存在此故障链
```

#### 进阶：反向求解安全配置

```python
def find_safe_config(base_config, fault_pattern, k=5):
    """不是找故障，而是找'什么配置能让故障路径不存在'"""
    solver = Z3()
    
    config = {
        "cache_replicas":          Symbolic(int, min=1, max=10),
        "model_store_conn_pool":   Symbolic(int, min=50, max=500),
        "retry_max_attempts":      Symbolic(int, min=0, max=5),
        "circuit_breaker_threshold": Symbolic(float, min=0.1, max=0.9),
    }
    
    # 要求：不存在 k 步内的故障路径
    solver.add(NOT(encode_fault_reachable(config, fault_pattern, k)))
    
    if solver.check() == SAT:
        return solver.model()
        # "cache ≥ 3 副本、conn_pool ≥ 200、max_retry ≤ 2 时安全"
    else:
        return "无论怎么配置都无法避免此故障模式"
```

---

## 3. 方法选择指南

| SRE 场景 | 推荐方法 | 原因 |
|----------|---------|------|
| 验证已有 runbook / SOP | Model Checking | M 已知，只需判定 |
| 判断需求是否自相矛盾 | Realizability Check | 在投入实现之前先确认可行性 |
| 自动生成 rollout controller | Reactive Synthesis | 只写规约，输出 correct-by-construction 的状态机 |
| 检测已知故障模式是否可触发 | Bounded Model Checking | 有界搜索，适合实际故障链长度 |
| SOP 验证 + 修复 | 三者组合 | Realizability → Model Check → Synthesis |
| 反向求解安全配置 | BMC 逆向 | 找使故障路径不存在的配置参数 |

---

## 4. 核心前提

这套技术的瓶颈不在算法，而在于**能否把业务语义精确地形式化**。SRE 领域天然适合：

- SLO 天然就是量化的规约
- 变更步骤天然就是离散的状态机
- 监控指标天然就是环境输入
- 故障传播规则可以从 postmortem 中系统性提炼

只要能说清楚业务的**约束、规约、目标**，这套技术就能发挥价值。
