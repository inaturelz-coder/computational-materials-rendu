# 第九篇 · 督脉第 4 阶段：UQ — 不确定性量化

*UQ 是督脉的"最后一公里"——给任脉每一层都加上置信区间*
*下游：ICME 在 UQ 信息上做工程决策*

## 第 36 章 UQ 基础与误差分类

### 31.1 不确定性的分类

**A. Aleatoric（随机不确定性）** — 数据内在噪声
- 不能消除
- 例：实验测量误差、原子热振动

**B. Epistemic（认知不确定性）** — 模型/参数不确定
- 可通过更多数据/更好模型减少
- 例：DFT 泛函选择、参数拟合不充分

CP-FEM 例：
- Aleatoric：实验 σ_y 标准差 ±15 MPa（同批样品）
- Epistemic：硬化参数 g_∞ 拟合误差 ±10 MPa

### 31.2 UQ 三大方法

**1. 蒙特卡洛**
- 抽 N 次参数 → 跑 N 次模拟 → 直方图
- 简单，收敛慢（√N）

**2. Polynomial Chaos Expansion（PCE）**
- 把响应 $y$ 展开成正交多项式：$y = \sum c_i \Psi_i(\xi)$
- 系数 $c_i$ 用回归/谱投影算
- 比 MC 快 10-100×（5 维以下）

**3. Surrogate-based**
- 训练 GP/NN 代理模型
- 在代理上做 MC（瞬秒完）
- 适合昂贵模拟

### 31.3 灵敏度分析（Sobol 指数）

**一阶 Sobol 指数**：
$$S_i = \frac{V_i}{V}, \quad V_i = \text{Var}(\mathbb{E}[Y|X_i])$$

**总 Sobol 指数**（含交互）：
$$S_i^T = 1 - \frac{V_{\sim i}}{V}$$

```python
from SALib.sample import sobol
from SALib.analyze import sobol as analyze_sobol

problem = {
    "num_vars": 4,
    "names": ["E", "nu", "sigma_y", "n_hard"],
    "bounds": [[150e9, 250e9], [0.25, 0.35], [200e6, 400e6], [0.1, 0.3]]
}

# 抽样
param_values = sobol.sample(problem, 1024)  # 1024 * (2*D+2) 次
# 跑模拟
Y = np.array([run_fem(p) for p in param_values])

# 分析
Si = analyze_sobol.analyze(problem, Y)
print("一阶 Sobol:", Si["S1"])
print("总 Sobol:", Si["ST"])
```

### 31.4 Conformal Prediction（无分布保证区间）

任何回归模型 + 校准集 → 90% 覆盖区间。

```python
from mapie.regression import MapieRegressor
from sklearn.ensemble import RandomForestRegressor

mapie = MapieRegressor(RandomForestRegressor(), cv=10)
mapie.fit(X_train, y_train)

y_pred, y_pi = mapie.predict(X_test, alpha=0.1)  # 90% CI
# y_pi shape: (n_test, 2, 1), lower/upper
```

**保证**：在测试集上，真值落入 [lower, upper] 的频率 ≥ 90%（无论模型对错）。

### 31.5 UQ 在多尺度链中传播

ICME 链：DFT 参数误差 → CALPHAD 拟合误差 → PF 微观组织误差 → CP-FEM 性质误差

**链式 UQ**：每尺度输出区间 → 上游用 GP/PCE 代理 + MC

例：DFT 弹性常数 C11 = 245 ± 5 GPa → CP-FEM 屈服强度 σ_y 误差贡献？
- 用 PCE 拟合 σ_y(C11)
- 抽 C11 ~ N(245, 5) 10000 次 → σ_y 直方图
- 结果：σ_y = 1180 ± 8 MPa（DFT 贡献 ~5%）

## 第 37 章 ESPEI 贝叶斯拟合 CALPHAD

### 32.1 数据集成

ESPEI 把多种数据合并：
- 单元素 SGTE
- 二元相图测点（X_eq, T）
- 三元 DSC 量热
- DFT 形成焓
- 实验活度

### 32.2 似然函数

每数据点：
$$\mathcal{L}_i \propto \exp\left(-\frac{(y_i^{obs} - y_i^{calc}(\theta))^2}{2 \sigma_i^2}\right)$$

总：$\mathcal{L} = \prod \mathcal{L}_i$

### 32.3 ESPEI 工作流

```bash
# 1. 准备数据
mkdir Ni-Cr
# 写入 phase_diagram.json, formation_enthalpy.json, etc.

# 2. 单步生成初始 TDB
espei --input input-mcmc-skip.yaml
# Yields Ni-Cr.tdb (deterministic fit)

# 3. MCMC
espei --input input-mcmc.yaml
# Yields trace.npy, lnprob.npy, Ni-Cr_MCMC.tdb
```

input-mcmc.yaml：
```yaml
system:
  phase_models: phases.json
  datasets: input-data
generate_parameters:
  excess_model: linear
  ref_state: SGTE91
mcmc:
  iterations: 5000
  prior:
    name: normal
    sigma: 0.5  # 相对参数值的标准差
```

### 32.4 后验分析

```python
import numpy as np
trace = np.load("trace.npy")  # (n_walkers, n_steps, n_params)
flat_samples = trace[:, 1000:, :].reshape(-1, trace.shape[-1])

# 每参数中位 + 16-84 区间
for i, name in enumerate(param_names):
    med = np.median(flat_samples[:, i])
    low, high = np.percentile(flat_samples[:, i], [16, 84])
    print(f"{name}: {med:.1f} (+{high-med:.1f}/-{med-low:.1f})")

# 相图后验（包络）
T_range = np.linspace(800, 1800, 100)
phases_lo, phases_hi = compute_phase_diagram_envelope(flat_samples[::10], T_range)
plt.fill_between(T_range, phases_lo, phases_hi, alpha=0.3, label="68% CI")
```

## 第 38 章 多保真度 UQ

### 33.1 多保真度采样

不同精度模型混用：
- HF（高保真）：贵但准（DFT GGA）
- LF（低保真）：便宜但偏（empirical potential）

**MFMC（Multi-fidelity Monte Carlo）**：
$$\bar{y}^{MFMC} = \bar{y}^{HF} + \alpha (\bar{y}^{LF} - \mathbb{E}[Y^{LF}])$$

最优 α 来自 HF-LF 相关系数。

**Co-Kriging**：HF 与 LF 联合训练 GP。

```python
import emukit
from emukit.multi_fidelity import GPyMultiOutputWrapper
from emukit.multi_fidelity.models import GPyLinearMultiFidelityModel

# 数据
X_train = [(X_LF, X_HF), ...]
Y_train = [(Y_LF, Y_HF), ...]

# 训练
kernel = LinearMultiFidelityKernel([GPy.kern.RBF(1) for _ in range(2)])
model = GPyLinearMultiFidelityModel(X_train, Y_train, kernel, n_fidelities=2)
model.optimize()

# 预测（高保真）
y_pred, y_var = model.predict(X_test, fidelity=1)
```

## 第 39 章 UQ 实战案例

### 34.1 CALPHAD Ni-Al 后验包络

用 ESPEI MCMC 拟合 Ni-Al，输出 5000 个 posterior 参数样本。每样本算相图。

结果：
- γ' 析出温度后验：1190 ± 15 K
- 与实验（1185-1200 K）一致
- 极少数样本预测异常相 → 这些样本应排除（先验不严格）

### 34.2 CP-FEM 屈服强度 UQ

输入参数及其不确定性：
- C11: 245 ± 5 GPa (DFT)
- ρ_0 初始位错密度: 10^12 ± 10^11 m^-2
- 织构 J: 0.1 ± 0.05

跑 200 次 CP-FEM（每次 6 h）→ σ_y 后验：1180 ± 35 MPa

**结论**：织构是最大贡献（Sobol ST = 0.65），DFT 弹性常数贡献小（ST = 0.05）。

### 34.3 UQ → 决策

工程标准要求 σ_y > 1100 MPa with 95% confidence。后验中 P(σ_y > 1100) = ?

$$P = \int_{1100}^{\infty} p(\sigma_y) d\sigma_y \approx \frac{1}{N} \sum_i \mathbb{1}[\sigma_y^i > 1100]$$

样本中 192/200 满足 → P = 96%，超过 95% 标准 → 通过验收。

---


