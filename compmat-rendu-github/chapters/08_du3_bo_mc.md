# 第八篇 · 督脉第 3 阶段：BO + MC + 主动学习

*上游：ML 模型 + 不确定度*
*下游：决定"下一个实验/计算做什么最值"——把任脉的算力投到最值得算的地方*

## 第 32 章 高斯过程深度

### 27.1 GP 的概率视角

高斯过程不是"一个函数"，而是"函数的分布"：

$$f(x) \sim \mathcal{GP}(m(x), k(x, x'))$$

意思：对任意有限点集 $\{x_1, ..., x_n\}$，$[f(x_1), ..., f(x_n)]^T$ 是多变量高斯分布。

**直观**：在没见过的点，函数值有"先验分布"，先验由 mean function $m$ + kernel $k$ 决定。

### 27.2 后验推断完整推导

给定训练数据 $(X, y)$ 和测试点 $X_*$：

**联合先验**（假设 $m=0$）：
$$\begin{bmatrix} y \\ f_* \end{bmatrix} \sim \mathcal{N}\left(0, \begin{bmatrix} K + \sigma_n^2 I & K_* \\ K_*^T & K_{**} \end{bmatrix}\right)$$

其中 $K_{ij} = k(x_i, x_j)$，$K_* = k(X, X_*)$，$K_{**} = k(X_*, X_*)$。

**后验**（用高斯条件公式）：
$$f_* | X, y, X_* \sim \mathcal{N}(\mu_*, \Sigma_*)$$

$$\boxed{\mu_* = K_*^T (K + \sigma_n^2 I)^{-1} y}$$
$$\boxed{\Sigma_* = K_{**} - K_*^T (K + \sigma_n^2 I)^{-1} K_*}$$

**关键观察**：
- $\mu_*$ 是训练点 $y$ 的加权平均，权重由 kernel 决定
- $\Sigma_*$ 与训练数据 $y$ 无关，只看 $X$（这是 GP 主要特征：方差只反映"信息匮乏"）

### 27.3 Kernel 选择指南

| Kernel | 形式 | 平滑度 | 用途 |
|--------|------|--------|------|
| RBF (squared exp) | $\exp(-\|x-x'\|^2 / 2l^2)$ | $C^\infty$ | 默认，最平滑 |
| Matern 3/2 | $(1+\sqrt{3}r/l)\exp(-\sqrt{3}r/l)$ | $C^1$ | 1 次可导，物理常用 |
| Matern 5/2 | $(1+\sqrt{5}r/l+5r^2/3l^2)\exp(-\sqrt{5}r/l)$ | $C^2$ | 2 次可导，工程常用 |
| Linear | $x^T x'$ | - | 线性问题 |
| Periodic | $\exp(-2\sin^2(\pi(x-x')/p)/l^2)$ | - | 周期信号 |

**ARD（Automatic Relevance Determination）**：每维独立 lengthscale，可自动发现"哪个维度重要"。

### 27.4 超参数优化（边缘似然最大化）

$$\log p(y|X, \theta) = -\frac{1}{2} y^T (K + \sigma_n^2 I)^{-1} y - \frac{1}{2} \log|K + \sigma_n^2 I| - \frac{n}{2} \log 2\pi$$

三项的含义：
- 第一项：数据拟合（小残差好）
- 第二项：模型复杂度（kernel 越平滑越好）
- 第三项：常数

**自动 Occam's razor**：边缘似然惩罚过复杂模型。

```python
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel

# 数据：合金组分 → 强度
X = np.array([[0.1, 0.2, 0.0], [0.3, 0.1, 0.1], ...])  # (n_samples, 3)
y = np.array([850, 920, ...])  # 强度 MPa

# Kernel: 常数 × Matern + 噪声
kernel = ConstantKernel(1.0) * Matern(length_scale=[1.0]*3, nu=2.5) \
         + WhiteKernel(noise_level=10**2)

gp = GaussianProcessRegressor(
    kernel=kernel, normalize_y=True,
    n_restarts_optimizer=10  # 多次随机初始避免局部极小
)
gp.fit(X, y)
print(gp.kernel_)  # 显示训练后的 lengthscale, noise

# 预测含方差
X_new = np.array([[0.2, 0.15, 0.05]])
mu, std = gp.predict(X_new, return_std=True)
print(f"预测强度: {mu[0]:.1f} ± {std[0]:.1f} MPa")
```

## 第 33 章 贝叶斯优化全套

### 28.1 BO 完整算法

```
输入: 初始样本 D_0, 目标 f (黑盒), 搜索域 X, 预算 N
循环 t = 1, 2, ..., N:
    1. 训练 GP: 用 D_{t-1} 拟合后验
    2. 构造 acquisition function: α(x | D_{t-1})
    3. 优化: x_t = argmax_{x ∈ X} α(x | D_{t-1})
    4. 评估: y_t = f(x_t) (跑实验/DFT)
    5. 更新: D_t = D_{t-1} ∪ {(x_t, y_t)}
返回: x* = argmax y_i
```

### 28.2 Acquisition Function 详细

**EI（Expected Improvement）**：
$$\text{EI}(x) = \mathbb{E}[\max(f(x) - f^+, 0)]$$
其中 $f^+ = \max_i y_i$（当前最好值）。

解析解（假设最大化）：
$$\text{EI}(x) = (\mu(x) - f^+ - \xi) \Phi(Z) + \sigma(x) \phi(Z)$$
其中 $Z = (\mu(x) - f^+ - \xi) / \sigma(x)$，$\xi \geq 0$ 是探索-开采参数（典型 0.01）。

**UCB（Upper Confidence Bound）**：
$$\text{UCB}(x) = \mu(x) + \kappa \sigma(x)$$
$\kappa$ 控制探索（典型 2-5）。$\kappa = 0$ 纯开采；$\kappa \to \infty$ 纯探索。

**PI（Probability of Improvement）**：
$$\text{PI}(x) = \Phi\left(\frac{\mu(x) - f^+ - \xi}{\sigma(x)}\right)$$
只考虑"概率"不考虑"幅度"，不如 EI。

**TS（Thompson Sampling）**：
从后验抽一个样本函数 $\tilde{f}(x)$，最大化 $\tilde{f}$。简单但有效，适合并行 BO。

**KG（Knowledge Gradient）**：
评估"如果我跑了这一点，下一步选择会变好多少"。比 EI 长远，但 10× 计算量。

### 28.3 多目标 BO

材料常需平衡多目标（强度+延展性、能量+稳定性）。

**Pareto Front**：不能同时改进两目标的点集。

**EHVI（Expected Hypervolume Improvement）**：
$$\text{EHVI}(x) = \mathbb{E}[\text{HV}(P \cup \{f(x)\}) - \text{HV}(P)]$$
其中 $P$ 当前 Pareto front，HV 是 hypervolume（参考点围的"超体积"）。

```python
import torch
from botorch.models import SingleTaskGP, ModelListGP
from botorch.acquisition.multi_objective import qExpectedHypervolumeImprovement
from botorch.utils.multi_objective.box_decompositions import NondominatedPartitioning
from botorch.optim import optimize_acqf

# 两目标：强度 (max), 延展性 (max)
train_X = torch.tensor([[...], ...])
train_Y = torch.tensor([[850, 12], [920, 8], ...])  # (n, 2)

# 每个目标一个 GP
models = [SingleTaskGP(train_X, train_Y[:, i:i+1]) for i in range(2)]
model = ModelListGP(*models)

# 参考点（差于所有候选）
ref_point = torch.tensor([600.0, 5.0])
partitioning = NondominatedPartitioning(ref_point=ref_point, Y=train_Y)

acq = qExpectedHypervolumeImprovement(
    model=model, ref_point=ref_point, partitioning=partitioning
)

# 一次提一批 q 个候选（并行实验）
candidates, _ = optimize_acqf(
    acq, bounds=torch.tensor([[0]*5, [1]*5]),
    q=4, num_restarts=10, raw_samples=512
)
```

### 28.4 约束 BO

材料设计往往有约束（成本 < $X$、相稳定性 > Y）。

**EIC（Expected Improvement with Constraints）**：
$$\text{EIC}(x) = \text{EI}(x) \cdot \prod_i \text{Pr}(g_i(x) \leq 0)$$

约束也建模 GP，乘上"约束被满足的概率"。

### 28.5 高维 BO 技巧

GP 在 $d > 20$ 退化。常用方法：

**TuRBO**（Trust Region BO）：分块小信赖域搜索
**SAASBO**（Sparse Axis-Aligned Subspace）：自动找重要维度
**LineBO**：每步沿一个方向搜索
**Bayesian NN as surrogate**：换 BNN 替代 GP

### 28.6 BO 案例：高熵合金强度优化

5 元 HEA：Fe-Co-Ni-Cr-Mn，各 0-1 mole fraction，约束 $\sum = 1$。

```python
from botorch.models import SingleTaskGP
from botorch.acquisition import qExpectedImprovement
from botorch.optim import optimize_acqf
import torch

# 初始 10 组 DFT/实验
train_X = torch.rand(10, 5); train_X /= train_X.sum(1, keepdim=True)
train_Y = run_dft(train_X)  # 用户函数

for iteration in range(20):
    gp = SingleTaskGP(train_X, train_Y)
    fit_gpytorch_mll(ExactMarginalLogLikelihood(gp.likelihood, gp))
    
    acq = qExpectedImprovement(gp, best_f=train_Y.max())
    
    # 约束: x_i ≥ 0, sum = 1
    cand, _ = optimize_acqf(
        acq, bounds=torch.stack([torch.zeros(5), torch.ones(5)]),
        q=2, num_restarts=10, raw_samples=512,
        equality_constraints=[(torch.arange(5), torch.ones(5), 1.0)]
    )
    
    new_y = run_dft(cand)
    train_X = torch.cat([train_X, cand])
    train_Y = torch.cat([train_Y, new_y])
    print(f"Iter {iteration}: best = {train_Y.max():.1f}")
```

## 第 34 章 MCMC 深度

### 29.1 为什么需要 MCMC

贝叶斯推断需要：
$$p(\theta | D) = \frac{p(D|\theta) p(\theta)}{p(D)}, \quad p(D) = \int p(D|\theta) p(\theta) d\theta$$

分母（证据）通常**无解析解**。MCMC 直接从 $p(\theta|D)$ **抽样**，不需要算 $p(D)$。

### 29.2 Metropolis-Hastings

```
1. 选 proposal q(θ'|θ_t) （如高斯）
2. 算接受概率:
   α = min(1, [p(D|θ') p(θ') q(θ_t|θ')] / [p(D|θ_t) p(θ_t) q(θ'|θ_t)])
3. 抽 u ~ U(0,1):
   if u < α: θ_{t+1} = θ' (接受)
   else: θ_{t+1} = θ_t (拒绝)
```

**关键**：分母 $p(D)$ 在 α 中消掉了（出现在 $p(\theta|D)$ 分子分母）。

### 29.3 HMC（Hamiltonian Monte Carlo）

MH 在高维"碰运气" → HMC 用梯度引导，效率高 10-100 倍。

**核心思想**：把 $\theta$ 当"位置"，引入辅助"动量" $p$。系统总能量：

$$H(\theta, p) = -\log p(\theta|D) + \frac{1}{2} p^T M^{-1} p$$

按 Hamilton 方程积分（leapfrog）一段时间 → 提议 → MH 接受。

**NUTS**（No-U-Turn Sampler）：自动选积分步数，是 Stan / PyMC 默认。

### 29.4 Burn-in 与诊断

**Burn-in**：链未收敛前的样本，扔掉（典型前 25%）。

**诊断**：
- Trace plot：应像"白噪声"，无明显趋势
- ESS（Effective Sample Size）：去自相关后的有效样本数。每参数 ESS > 400 算够
- $\hat{R}$（Gelman-Rubin）：多链方差/链内方差。<1.01 视为收敛
- Autocorrelation：滞后 50 步内应衰减到 0

### 29.5 emcee 拟合 CALPHAD 参数

```python
import emcee
import numpy as np

def log_prior(theta):
    L0, L1, L2 = theta
    if -50000 < L0 < 50000 and -20000 < L1 < 20000 and -10000 < L2 < 10000:
        return 0.0  # flat prior
    return -np.inf

def log_likelihood(theta, x_data, G_data, sigma):
    L0, L1, L2 = theta
    G_pred = L0 * x_data * (1 - x_data) + L1 * x_data * (1 - x_data) * (1 - 2*x_data) + L2 * (1 - 2*x_data)**2 * x_data * (1 - x_data)
    return -0.5 * np.sum(((G_data - G_pred) / sigma)**2)

def log_prob(theta, x_data, G_data, sigma):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, x_data, G_data, sigma)

# 32 walkers, 3 维
n_walkers, n_dim = 32, 3
p0 = np.random.randn(n_walkers, n_dim) * 1000  # 初始小扰动
sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_prob, args=(x_data, G_data, sigma))

print("Burn-in...")
state = sampler.run_mcmc(p0, 1000)
sampler.reset()

print("Production...")
sampler.run_mcmc(state, 5000, progress=True)

# 分析
samples = sampler.get_chain(flat=True)  # (160000, 3)
print(f"L0 = {np.median(samples[:,0]):.0f} ± {np.std(samples[:,0]):.0f}")
print(f"acceptance: {np.mean(sampler.acceptance_fraction):.2f}")  # 应 ~0.3

# 后验图
import corner
corner.corner(samples, labels=["L0", "L1", "L2"], show_titles=True)
```

### 29.6 MC 与材料模拟

材料里 MC 有两个不同用法：

**用法 A：参数推断（贝叶斯）** — 上面的 emcee 示例

**用法 B：构型采样（统计力学）**
- Metropolis Monte Carlo：固定 T，从 Boltzmann 分布 $\propto \exp(-E/kT)$ 抽样
- Kinetic Monte Carlo（KMC）：基于跳跃率，模拟时间演化（扩散、相变形核）
- Wang-Landau：估计态密度 g(E)

```python
# Metropolis MC 模拟 Ising 模型（磁性相变）
import numpy as np

N, J = 50, 1.0
spins = 2 * np.random.randint(0, 2, (N, N)) - 1

def metropolis_step(spins, beta):
    for _ in range(N*N):
        i, j = np.random.randint(0, N, 2)
        neighbors = spins[(i+1)%N, j] + spins[(i-1)%N, j] + spins[i, (j+1)%N] + spins[i, (j-1)%N]
        dE = 2 * J * spins[i,j] * neighbors
        if dE < 0 or np.random.random() < np.exp(-beta * dE):
            spins[i,j] *= -1
    return spins

for T in np.linspace(0.5, 4.0, 30):
    beta = 1/T
    for _ in range(1000): spins = metropolis_step(spins, beta)
    M = np.abs(spins.mean())
    print(f"T={T:.2f}, |M|={M:.3f}")
# 临界温度 T_c ≈ 2.27 J/k (Onsager)
```

## 第 35 章 主动学习闭环

### 30.1 主动学习完整框架

```
设计空间 X (10^6 候选)
  ↓ 初始抽 N0 = 20 个 (Latin Hypercube)
跑 DFT / 实验 → 训练数据 D_0
  ↓
循环 (预算 = N 次):
  1. 训练 surrogate (GP / MLP / GNN) 
  2. 用 surrogate 预测 X 中所有点
  3. 计算 acquisition (EI / UCB / variance)
  4. 选 batch q 个最高得分点
  5. 跑 DFT / 实验 → 加入 D
最终: 找到最优 + 整张性质表
```

### 30.2 Batch BO 多样性约束

为避免一次选 4 个"凑一起"的点，加多样性：

**qNEI（Noisy EI）**：联合优化 q 个点的 joint EI
**DPP（Determinantal Point Process）**：用 kernel 矩阵的 determinant 选有多样性的批
**Hallucination**：选 1 个后假装结果是 GP 均值，再选下一个

### 30.3 端到端材料发现案例

**目标**：从 12 种元素的 4 元合金（10^6 候选）找最高屈服强度。

```python
import numpy as np, torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import qExpectedImprovement
from botorch.optim import optimize_acqf_discrete

# 1. 构造候选空间
elements = ["Fe", "Co", "Ni", "Cr", "Mn", "V", "Mo", "Nb", "Ti", "Al", "Si", "Cu"]
candidates = []
for combo in combinations(elements, 4):
    for frac in lattice_grid(0.1):  # 0.1 步长四元单纯形
        candidates.append((combo, frac))
print(f"{len(candidates)} 候选")  # ~10^6

# 2. 特征化（matminer Magpie）
X_all = featurize(candidates)  # (1e6, 132)

# 3. 初始 20 个 (Latin Hypercube)
idx0 = lhs_sample(len(candidates), 20)
X_obs = X_all[idx0]
y_obs = run_experiments(candidates[idx0])  # 屈服强度

# 4. 主动学习 30 轮（每轮 5 个 batch）
for round in range(30):
    X_t = torch.tensor(X_obs); y_t = torch.tensor(y_obs)[:, None]
    gp = SingleTaskGP(X_t, y_t)
    fit_gpytorch_mll(ExactMarginalLogLikelihood(gp.likelihood, gp))
    
    acq = qExpectedImprovement(gp, best_f=y_obs.max())
    new_idx, _ = optimize_acqf_discrete(acq, q=5, choices=torch.tensor(X_all))
    
    new_y = run_experiments([candidates[i] for i in new_idx])
    X_obs = np.vstack([X_obs, X_all[new_idx]])
    y_obs = np.concatenate([y_obs, new_y])
    print(f"Round {round}: best = {y_obs.max():.1f} MPa, 实验数 = {len(y_obs)}")

# 总实验: 20 + 30*5 = 170 (vs 10^6 候选)
```

### 30.4 习题与答案

**习题 27.1**：GP 后验方差 $\Sigma_*$ 与训练 $y$ 无关，意味着什么？

**答**：意味着我们能在"未跑实验前"就知道每一点的不确定性。这是主动学习的核心：选不确定性最大的点 = 不需要先知道 $y$。

**习题 28.1**：为什么 BO 通常用 EI 而不是直接最大化 $\mu(x)$？

**答**：直接最大化 $\mu$ 是"纯开采"，会卡在局部极大。EI 同时考虑 $\mu$ 和 $\sigma$，自动在"近期收益"和"信息探索"之间平衡。$\xi$ 参数可调控制开采-探索倾向。

**习题 29.1**：MCMC 链的接受率应该多少？

**答**：经验：1 维 ~0.45，高维 ~0.23（Roberts-Gelman-Gilks 1997 理论）。过高 = proposal 太小（链动不了）；过低 = proposal 太大（总被拒）。emcee 用 ensemble 自适应，目标 0.2-0.5。

**习题 30.1**：主动学习里 batch size $q$ 怎么选？

**答**：$q$ 与"并行能力"匹配。如有 5 台 DFT 服务器，$q=5$。但 $q$ 越大，batch 内多样性越关键（否则浪费）。典型工业 $q=4-8$。


