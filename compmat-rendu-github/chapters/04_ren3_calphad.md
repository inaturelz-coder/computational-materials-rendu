# 第四篇 · 任脉第 3 步：热力学层 — CALPHAD

*上游：DFT 提供端元能；MD 提供有限温修正*
*下游：Phase-field 用 CALPHAD 的 G(x, T) 作为体能自由能函数*

## 第 14 章 热力学基础回顾

### 14.1 热力学势 — 5 个核心势

材料计算中，**Gibbs 能 G** 最常用，但理解所有 5 个势的关系很重要：

| 势 | 自变量 | 何时用 |
|---|---|---|
| 内能 U | S, V, N | 孤立系统 |
| 焓 H = U + PV | S, P, N | 等压过程 |
| Helmholtz F = U - TS | T, V, N | 等温等容 |
| **Gibbs G = H - TS** | T, P, N | **等温等压 — CALPHAD 默认** |
| 巨势 Ω = F - μN | T, V, μ | 开放系统 |

**Legendre 变换** 把一组变量换成另一组：

$$ G(T, P, N) = U - TS + PV = F + PV = H - TS $$

### 14.2 G 的微分形式

$$ dG = -SdT + VdP + \sum_i \mu_i dN_i $$

这给出 **Maxwell 关系**：

$$ S = -\left(\frac{\partial G}{\partial T}\right)_{P, N_i} $$
$$ V = \left(\frac{\partial G}{\partial P}\right)_{T, N_i} $$
$$ \mu_i = \left(\frac{\partial G}{\partial N_i}\right)_{T, P, N_{j\neq i}} $$

**实战意义**：
- 知道 G(T, P, x) → 算 S, V, μ_i 全部
- CALPHAD 给 G，自动给所有热力学性质

### 14.3 化学势深度

**理想气体**：

$$ \mu_i^{ig}(T, P, x_i) = \mu_i^0(T) + RT\ln\frac{x_i P}{P^0} $$

**理想溶液**：

$$ \mu_i^{ideal}(T, P, x_i) = \mu_i^0(T, P) + RT\ln x_i $$

**实际溶液**（用 activity coefficient γ_i）：

$$ \mu_i = \mu_i^0 + RT\ln(\gamma_i x_i) = \mu_i^0 + RT\ln a_i $$

**部分摩尔量** (Partial molar property):

$$ \bar{Y}_i = \left(\frac{\partial Y}{\partial n_i}\right)_{T,P,n_{j\neq i}} $$

For Gibbs energy: $\bar{G}_i = \mu_i$.

### 14.4 Gibbs-Duhem relation

$$ \sum_i n_i d\mu_i = -SdT + VdP $$

**实际意义**：
- T, P 固定时，所有化学势变化不独立
- 一相中：$\sum x_i d\mu_i = 0$
- 给我们一个 constraint，实验数据 fitting 用

### 14.5 多相平衡

**核心原理**：相 α 和 β 平衡时

$$ \mu_i^\alpha = \mu_i^\beta \quad \text{for all } i $$

**几何 picture**: **共同切线 (common tangent)** 法则

```
G
|
|     G_α        G_β
|      \        /
|       \      /
|     ---\----/---  <- common tangent
|         \  /
|          \/
+-------------------> x
```

切线斜率 = 化学势，截距 = 物质 0 / 1 时化学势。

### 14.6 Gibbs Phase Rule

**自由度 F = C - P + 2**

- C = 组分数
- P = 相数
- 2 = T 和 P

**例**：
- 单相纯组分: F = 1-1+2 = 2（T, P 任选）
- 共晶不变点（C=2, P=3）: F = 2-3+2 = 1, 但 P 通常固定 → F = 0
- 三元三相: F = 3-3+2 = 2（T, P 还有一变）

### 14.7 简单二元相图分析

**二元 A-B isomorphous** (完全互溶):

液相和固相 G 函数 vs x_B：
- 高 T: liquid 全程低
- 低 T: solid 全程低
- 中间 T: tie line between liquid + solid

**二元共晶** (不完全互溶):
- 两固相（α and β）
- 液相 G 在 eutectic T 接触两 solid G

### 14.8 二元相图算 worked example

**Fe-Cr binary** at T=1000K:

PyCalphad code:

```python
from pycalphad import Database, equilibrium, variables as v
import numpy as np

dbf = Database("Fe-Cr.tdb")

T = 1000
results = []
x_Cr_range = np.linspace(0.01, 0.99, 50)

for x_Cr in x_Cr_range:
    eq = equilibrium(
        dbf,
        components=['FE', 'CR', 'VA'],
        phases=['BCC_A2', 'FCC_A1', 'SIGMA'],
        conditions={v.T: T, v.P: 101325, v.X('CR'): x_Cr}
    )
    # Get stable phases
    stable = eq.Phase.values[eq.NP.values > 1e-6]
    results.append({'x_Cr': x_Cr, 'phases': stable})

# Print phase boundaries
for r in results:
    if len(set(r['phases'])) > 1:
        print(f"x_Cr={r['x_Cr']:.3f}: {set(r['phases'])}")
```

输出会显示 BCC ↔ BCC+σ ↔ σ ↔ σ+BCC ↔ BCC（典型 Fe-Cr at 1000K）.

### 14.9 习题（含答案要点）

**习题 14.1**: 推导 Gibbs-Duhem.
**答案**: 对 G = ΣN_i μ_i 求 dG，与 第一定律 + chain rule 比较.

**习题 14.2**: Fe-C system at 1100K, x_C=0.005. Phase 鉴定 + lever rule.
**答案**: γ (FCC) + α (BCC) 两相; 用 PyCalphad 算 amounts.

**习题 14.3**: 解释为什么相变温度下 ΔG = 0 而 ΔH ≠ 0.
**答案**: 相变温度 G_α = G_β, 所以 ΔG = 0. 但 ΔH = T·ΔS ≠ 0 (latent heat).

**习题 14.4**: 二元 isomorphous 中 lens 形状 ↔ 何时变 "deep eutectic"?
**答案**: 当 |L_solid - L_liquid| 大时 → minimum 出现.

**习题 14.5**: Compute partial molar entropy of A in A-B liquid at any T, x.
**答案**: $\bar{S}_A = -(\partial \mu_A / \partial T)_{P,x}$.

## 第 15 章 CALPHAD 方法论

### 15.1 历史与起源

**Larry Kaufman** in 1970s saw the gap:
- DFT 太昂贵 + 0K only
- 实验 数据零散 + 不能内插
- 工程需要 multi-component

**解决方案**: 用**参数化 G 函数** + 实验拟合 → 然后 minimize G → 相图.

**Kaufman 1970** book 是起点.

**SGTE database** (1990s): 标准 element data.

**现代**: CALPHAD assessments + 1000+ binary systems + 商业数据库（TCFE, TCNI, TCAL...）.

### 15.2 CALPHAD assessment workflow

**完整 5 步**：

**1. 文献综述**:
- 收集相图（DTA, 金相, X-ray）
- 收集 thermodynamic data (calorimetry, vapor pressure, EMF)
- 评估 data quality

**2. 模型选择**:
- 每相 G 函数 form (RK, sublattice)
- 取决于相 structure + 物理 understanding

**3. DFT 输入**:
- End-member energies
- Mixing enthalpies
- Compound formation energies

**4. 参数 fitting**:
- Bayesian optimization (ESPEI)
- Least squares (PARROT)
- 不确定性 quantification

**5. Validation**:
- Cross-validation
- Independent data
- DFT comparison

### 15.3 TDB 文件深度

完整 TDB structure:

```
$ -------------------- ELEMENT --------------------
$ Name      Phase   M       H_298    S_298
ELEMENT FE    BCC_A2  55.847  4489.0   27.28
ELEMENT C     GRAPHITE 12.011 1054.0   5.74

$ -------------------- FUNCTIONS --------------------
$ Reference state Gibbs energies
FUNCTION GHSERFE 298.15 
  +1224.83 + 124.134*T - 23.5143*T*LN(T)
  -0.00439752*T**2 - 5.8927E-8*T**3 + 77358.5/T;
  1811.00 Y
  -25383.581 + 299.31255*T - 46*T*LN(T)
  +2.29603E31*T**(-9);
  6000.00 N!

FUNCTION GHSERCC 298.15
  -17368.441 + 170.73*T - 24.3*T*LN(T)
  -4.723E-4*T**2 + 2562600/T - 2.643E8/T**2 + 1.2E10/T**3;
  6000.00 N!

$ -------------------- PHASES --------------------
PHASE BCC_A2 %B 2 1 3 !
CONSTITUENT BCC_A2: FE,C : VA : !

PARAMETER G(BCC_A2,FE:VA;0)    298.15 +GHSERFE; 6000 N!
PARAMETER G(BCC_A2,C:VA;0)     298.15 +GHSERCC+322050+75.667*T; 6000 N!
PARAMETER L(BCC_A2,FE,C:VA;0)  298.15 -190T; 6000 N!
PARAMETER TC(BCC_A2,FE:VA;0)   298.15 1043; 6000 N!
PARAMETER BMAGN(BCC_A2,FE:VA;0) 298.15 2.22; 6000 N!
```

**重要 keywords**:
- `GHSERX`: Gibbs energy of X in stable element reference (SER)
- `PARAMETER G(phase,sublattice;v)`: vth order parameter
- `PARAMETER L`: excess Gibbs parameter
- `TC, BMAGN`: Curie T, magnetic moment (Inden model)

### 15.4 软件深度对比

**Thermo-Calc** (industry standard):
- 完整 GUI + scripting
- TCFE / TCNI / TCAL / TCSS / TCAQ databases
- DICTRA module for diffusion
- TC-Python API (modern)
- 商业 license €5000+ /year

**Pandat**:
- Strong in multi-component
- Pandat Python API
- CompuTherm databases
- 商业

**FactSage** (氧化物专长):
- 玻璃 / slags / 钢的氧化物
- 商业

**PyCalphad** (open):
- 完全免费
- Python native
- Active development
- Github + ESPEI for fitting
- Less polished but mostly capable

**OpenCalphad** (open):
- Fortran legacy
- Open source
- Powerful but unfriendly

### 15.5 案例 — 建立简单 Fe-C TDB

**目标**: 创建 minimal Fe-C database.

**Step 1**: SGTE elements (download or write):

```
FUNCTION GHSERFE ... (SGTE Fe data)
FUNCTION GHSERCC ... (SGTE C data, graphite reference)
```

**Step 2**: Define phases:

```
PHASE LIQUID % 1 1!
CONSTITUENT LIQUID: FE,C : !

PHASE BCC_A2 %B 2 1 3!
CONSTITUENT BCC_A2: FE,C : VA : !

PHASE FCC_A1 %A 2 1 1!
CONSTITUENT FCC_A1: FE,C : VA : !

PHASE CEMENTITE %& 2 3 1!
CONSTITUENT CEMENTITE: FE : C : !

PHASE GRAPHITE % 1 1!
CONSTITUENT GRAPHITE: C : !
```

**Step 3**: End-member parameters (from DFT or SGTE):

```
PARAMETER G(LIQUID,FE;0)   298 +GHSERFE+13265-7.6*T; 6000 N!
PARAMETER G(LIQUID,C;0)    298 +GHSERCC+115000-30.86*T; 6000 N!
PARAMETER G(BCC_A2,FE:VA;0) 298 +GHSERFE; 6000 N!
PARAMETER G(BCC_A2,C:VA;0)  298 +GHSERCC+322050+75.667*T; 6000 N!
...
```

**Step 4**: Excess parameters (fit to data):

```
PARAMETER L(LIQUID,FE,C;0)    298 +57600-22.7*T; 6000 N!
PARAMETER L(BCC_A2,FE,C:VA;0) 298 -190T; 6000 N!
PARAMETER L(FCC_A1,FE,C:VA;0) 298 -34671; 6000 N!
```

**Step 5**: Test:

```python
from pycalphad import Database, equilibrium, variables as v

dbf = Database("my_FeC.tdb")
result = equilibrium(dbf, ['FE','C','VA'],
                     ['BCC_A2','FCC_A1','CEMENTITE','GRAPHITE','LIQUID'],
                     {v.T: 1000, v.P: 101325, v.X('C'): 0.04})
print(result)
```

### 15.6 ESPEI for automated fitting

```python
# espei_input.yaml
system:
  components: ['FE', 'CR', 'VA']
  phase_models: phase_models.json
mcmc:
  iterations: 50000
  prior: 'zero'
```

```bash
espei --input espei_input.yaml
```

Outputs posterior distribution of all parameters with UQ.

### 15.7 习题

**习题 15.1**: 解释为什么用 G 而不是 F.
**答案**: 实验 + 工业过程多在 P 固定 → G 自然.

**习题 15.2**: 给定 Fe-C TDB, calculate eutectic temperature.
**答案**: Use PyCalphad equilibrium across T range, find P=1 atm, three phases coexist.

**习题 15.3**: ESPEI vs manual fitting 的优劣.
**答案**: ESPEI: 自动 + UQ + reproducible. Manual: 经验 + 物理直觉. 现代研究两者结合.

**习题 15.4**: 设计 Fe-Cr-Ni TDB structure (no need to fill values).
**答案**: 3 elements + LIQUID, BCC, FCC, SIGMA phases. Sublattice models for SIGMA. Endmember + excess parameters needed.

## 第 16 章 Gibbs 能模型

### 16.1 纯组分 — SGTE 数据库

**Standard polynomial form**:

$$ G_i^0(T) = a + bT + cT\ln T + dT^2 + eT^3 + \frac{f}{T} + ... $$

**Multiple temperature ranges**:

例：Fe pure
- 298-1811 K: BCC stable, polynomial 1
- 1811-6000 K: liquid stable, polynomial 2
- Continuous at 1811 K (Fe melting)

**Magnetic 贡献** (Inden formalism for ferromagnetic phases):

$$ G^{mag} = RT \ln(\beta + 1) f(\tau) $$

$$ \tau = T/T_C $$

$$ f(\tau) = 1 - \left[\frac{79\tau^{-1}}{140p} + \frac{474}{497}\left(\frac{1}{p} - 1\right)\left(\frac{\tau^3}{6} + \frac{\tau^9}{135} + \frac{\tau^{15}}{600}\right)\right] / A \quad (\tau \leq 1) $$

$$ f(\tau) = -\left[\frac{\tau^{-5}}{10} + \frac{\tau^{-15}}{315} + \frac{\tau^{-25}}{1500}\right] / A \quad (\tau > 1) $$

参数:
- β: magnetic moment
- T_C: Curie temperature
- p: 0.4 (BCC) or 0.28 (FCC)

### 16.2 固溶体 — Substitutional model

**Regular solution**:

$$ G_m = x_A G_A^0 + x_B G_B^0 + RT(x_A \ln x_A + x_B \ln x_B) + L_0 x_A x_B $$

**Redlich-Kister** (general):

$$ G^{xs} = x_A x_B \sum_v L_v(T) (x_A - x_B)^v $$

- L_0: 对称
- L_1: 非对称
- L_2, L_3: 高阶

**温度依赖**:

$$ L_v(T) = A_v + B_v T + C_v T \ln T + ... $$

通常 L_v = A_v + B_v T 足够.

### 16.3 三元系 — Muggianu extrapolation

For ternary A-B-C, from binary:

$$ G_m^{ternary} = \sum_{i=A,B,C} x_i G_i^0 + RT \sum_i x_i \ln x_i + G^{xs,binary,extrapolated} + L_{ABC}^{ternary} x_A x_B x_C $$

- Binary contributions: from Muggianu interpolation
- Ternary parameter L_ABC: usually small

### 16.4 Sublattice model — 深度

**通用 form**: (X)_a (Y)_b (Z)_c ...

例 1: Ni₃Al = (Ni,Al)₃(Ni,Al)₁ (FCC with antisite defects)
例 2: NaCl = (Na,Va)₁(Cl,Va)₁ (with vacancies)
例 3: Spinel = (Fe,Mg)₁(Fe,Mg,Al)₂(O)₄

**Sublattice constituent fraction** y_i^s:

$$ y_i^s = \frac{n_i^s}{n^s} $$

**Gibbs energy** for two-sublattice (X,Y)_a (Z)_b:

$$ G_m = y_X^1 y_Z^2 G^{X:Z} + y_Y^1 y_Z^2 G^{Y:Z} + aRT(y_X^1 \ln y_X^1 + y_Y^1 \ln y_Y^1) + y_X^1 y_Y^1 y_Z^2 L^{X,Y:Z} $$

### 16.5 实例 — σ phase

σ phase in Fe-Cr system has complex sublattice:

$$ (Fe)_{10}(Cr)_4(Fe,Cr)_{16} $$

- 10 atoms in sublattice 1 (Fe only)
- 4 atoms in sublattice 2 (Cr only)
- 16 atoms in sublattice 3 (Fe-Cr mixture)
- Total: 30 atoms/cell

Free energy in mixed sublattice:

$$ G^{Fe,Cr:Fe} = ... $$
$$ G^{Fe,Cr:Cr} = ... $$
$$ L^{Fe,Cr:Fe,Cr;0} = ... $$

### 16.6 Magnetic 贡献深度

**Inden-Hillert-Jarl model**:

```
TC: Curie/Néel temperature
β:  magnetic moment per atom
```

Both can have composition dependence:

```
PARAMETER TC(BCC_A2,FE:VA;0) 298 1043; 6000 N !
PARAMETER TC(BCC_A2,FE,CR:VA;0) 298 -1500; 6000 N !  
$ Cr lowers Fe Curie T
```

For AFM phases: TC negative + multiply by p.

### 16.7 Vacancy 处理

Many phases have vacancies. Sublattice with VA:

```
PHASE BCC_A2 %B 2 1 3!
CONSTITUENT BCC_A2: FE,C : VA : !
```

Second sublattice "VA" means vacancies on interstitial sites.

Interstitial concentration x_C is from constituent fraction y_C:

$$ x_C = \frac{3 y_C^2}{1 + 3 y_C^2} $$

（Because 3 VA sites per 1 substitutional）.

### 16.8 习题

**习题 16.1**: 写出 binary regular solution G_m, find x_critical for spinodal.
**答案**: $G_m = ... + L_0 x_A x_B$. Spinodal when $\partial^2 G / \partial x^2 = 0$.

**习题 16.2**: For (Ni,Al)_3 (Ni,Al)_1 = Ni3Al L1_2, write G expression with 4 end-members.
**答案**: 4 endmembers: Ni:Ni, Ni:Al, Al:Ni, Al:Al. Each has its own G_endmember. Mixing terms + RK among them.

**习题 16.3**: Why Inden formula switches at T_C?
**答案**: Below T_C: long-range order partly intact. Above T_C: short-range correlations decay.

**习题 16.4**: Compute x_C for y_C = 0.04 in BCC interstitial.
**答案**: x_C = 3·0.04² / (1+3·0.04²) ≈ 0.0048 ≈ 0.48 wt%

## 第 17 章 CALPHAD 实战

### 17.1 PyCalphad complete tutorial

**Installation**:

```bash
pip install pycalphad
# Or: conda install -c msys2 -c conda-forge pycalphad
```

**Basic equilibrium**:

```python
from pycalphad import Database, equilibrium
import pycalphad.variables as v
import numpy as np

# Load database
dbf = Database("FeCrNi.tdb")

# Components and phases
components = ['FE', 'CR', 'NI', 'VA']
phases = ['BCC_A2', 'FCC_A1', 'SIGMA', 'LIQUID']

# Single calculation
result = equilibrium(
    dbf, components, phases,
    {v.T: 1273, v.P: 101325, v.X('CR'): 0.18, v.X('NI'): 0.08}
)

# Print stable phases
mask = result.NP.values.squeeze() > 1e-6
print("Stable phases:")
for i, phase_name in enumerate(result.Phase.values.squeeze()):
    if mask[i]:
        amount = result.NP.values.squeeze()[i]
        print(f"  {phase_name}: {amount*100:.2f}%")
```

### 17.2 Phase diagram plotting

```python
from pycalphad import binplot
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
binplot(
    dbf, 
    components=['FE', 'CR', 'VA'],
    phases=['BCC_A2', 'FCC_A1', 'SIGMA', 'LIQUID'],
    conds={v.T: (300, 2000, 50), v.X('CR'): (0, 1, 0.02), v.P: 101325},
    ax=ax,
    plot_kwargs={'gridsize': 50}
)
plt.savefig("Fe-Cr_phase_diagram.png", dpi=200)
```

### 17.3 Multi-component phase fraction

```python
# Loop over composition
x_Cr_range = np.linspace(0.05, 0.25, 50)
results = {p: [] for p in phases}

for x_Cr in x_Cr_range:
    eq = equilibrium(
        dbf, components, phases,
        {v.T: 1373, v.P: 101325, v.X('CR'): x_Cr, v.X('NI'): 0.08}
    )
    phase_amounts = dict(zip(eq.Phase.values.squeeze(), eq.NP.values.squeeze()))
    for p in phases:
        results[p].append(phase_amounts.get(p, 0))

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
for p in phases:
    if max(results[p]) > 0.01:
        ax.plot(x_Cr_range, results[p], label=p, linewidth=2)
ax.set_xlabel('x(Cr)')
ax.set_ylabel('Phase fraction')
ax.legend()
plt.show()
```

### 17.4 Scheil-Gulliver solidification

**Theory**: 
- Solid: no diffusion (frozen)
- Liquid: perfect mixing
- Cool stepwise, in equilibrium at each step

```python
from pycalphad import calculate
import pandas as pd

def scheil_simulation(dbf, components, phases, x_init, T_start, T_end, dT=2):
    """Scheil cooling simulation"""
    T = T_start
    current_x = x_init.copy()
    f_liquid = 1.0
    
    results = []
    
    while T > T_end and f_liquid > 0.01:
        # Equilibrium at current T and composition
        eq = equilibrium(
            dbf, components, phases,
            {v.T: T, v.P: 101325, **{v.X(c): current_x[c] for c in components if c != 'VA'}}
        )
        
        # Get liquid amount
        liquid_idx = list(eq.Phase.values.squeeze()).index('LIQUID') if 'LIQUID' in eq.Phase.values.squeeze() else -1
        
        if liquid_idx == -1:
            break  # No liquid
        
        f_L_at_T = eq.NP.values.squeeze()[liquid_idx]
        
        if f_L_at_T < 0.01:
            break
        
        # Update liquid composition (in lever rule sense)
        # ... (simplified - full Scheil needs more careful implementation)
        
        results.append({
            'T': T,
            'f_liquid': f_liquid * f_L_at_T,
            **{f'x_{c}': current_x[c] for c in components if c != 'VA'}
        })
        
        T -= dT
    
    return pd.DataFrame(results)

# Example
df = scheil_simulation(
    dbf, ['AL', 'CU', 'VA'], ['LIQUID', 'FCC_A1', 'AL2CU'],
    {'AL': 0.96, 'CU': 0.04},
    T_start=950, T_end=500
)
```

### 17.5 化学势 + activity coefficient

```python
from pycalphad import calculate

calc = calculate(
    dbf, ['FE', 'C', 'VA'], 'FCC_A1',
    T=1100, P=101325,
    points=np.array([[0.95, 0.05, 1]])
)

# Get chemical potentials
mu_Fe = calc.MU.sel(component='FE').values.squeeze()
mu_C = calc.MU.sel(component='C').values.squeeze()

# Activity coefficient: γ_C = exp((μ_C - μ_C_ref - RT ln(x_C)) / RT)
R = 8.314
mu_C_ref = ...  # reference state
gamma_C = np.exp((mu_C - mu_C_ref - R*1100*np.log(0.05)) / (R*1100))
print(f"γ_C = {gamma_C:.3f}")  # ideal = 1
```

### 17.6 多元相图 — Ternary

```python
from pycalphad import ternplot

fig, ax = plt.subplots(figsize=(8, 6))
ternplot(
    dbf, components=['FE', 'CR', 'NI', 'VA'],
    phases=['BCC_A2', 'FCC_A1', 'SIGMA'],
    conds={v.T: 1273, v.P: 101325},
    x=v.X('CR'), y=v.X('NI'),
    ax=ax
)
```

### 17.7 ESPEI - automated parameter optimization

**Workflow**:

```yaml
# espei_in.yaml
system:
  phase_models: phase_models.json
  datasets: datasets/  # JSON files with experimental data
generate_parameters:
  excess_model: linear
  ref_state: 'SGTE91'
mcmc:
  iterations: 100000
  scheduler: 'dask'
  prior: 'normal'
output:
  output_db: 'output.tdb'
  tracefile: 'trace.npy'
  probfile: 'lnprob.npy'
```

**Run**:

```bash
espei --input espei_in.yaml
```

**Output**: 
- Optimized TDB
- Trace = posterior samples
- Plots for convergence + UQ

### 17.8 Industrial case study — Steel design

**Goal**: Design a steel with 0.4 wt% C, 1.5 wt% Mn, optimal tempering temperature for 400 HV.

```python
# Use Thermo-Calc TCFE database (or PyCalphad with simpler database)
from pycalphad import Database, equilibrium, variables as v

dbf = Database("TCFE12_subset.tdb")

# Define alloy
composition = {
    v.X('C'): 0.018,    # 0.4 wt% C (approximate to mole)
    v.X('MN'): 0.015,   # 1.5 wt% Mn
    v.X('FE'): 0.967    # balance
}

# Heat treatment study
T_range = np.linspace(700, 1100, 50) + 273.15

results = []
for T in T_range:
    eq = equilibrium(dbf, ['FE','C','MN','VA'], 
                    ['BCC_A2', 'FCC_A1', 'CEMENTITE', 'M23C6'],
                    {v.T: T, v.P: 101325, **composition})
    # Extract austenite (FCC) fraction
    # Carbon in austenite
    # ...
    results.append(...)
```

### 17.9 不确定性 quantification — Bayesian CALPHAD

```python
import emcee
import numpy as np

def log_likelihood(theta, T_exp, H_exp, H_err):
    """Log-likelihood for Fe-Cr mixing enthalpy"""
    L0, L1 = theta
    
    # CALPHAD model
    # For RK: H_mix = x(1-x) * [L0 + L1*(1-2x)]
    x = 0.5  # at equi-atomic
    H_model = x * (1-x) * (L0 + L1 * (1 - 2*x))
    
    return -0.5 * np.sum(((H_exp - H_model) / H_err)**2)

def log_prior(theta):
    L0, L1 = theta
    if -50000 < L0 < 50000 and -20000 < L1 < 20000:
        return 0
    return -np.inf

def log_posterior(theta, *args):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, *args)

# Run MCMC
nwalkers, ndim = 32, 2
p0 = np.random.randn(nwalkers, ndim) * 1000

sampler = emcee.EnsembleSampler(
    nwalkers, ndim, log_posterior,
    args=(T_exp_data, H_exp_data, H_err_data)
)

sampler.run_mcmc(p0, 10000, progress=True)
samples = sampler.get_chain(discard=2000, flat=True)

# Posterior summary
print(f"L0 = {samples[:,0].mean():.0f} ± {samples[:,0].std():.0f} J/mol")
print(f"L1 = {samples[:,1].mean():.0f} ± {samples[:,1].std():.0f} J/mol")

# Now compute phase diagram with uncertainty
# Sample N posterior parameters → run equilibrium → get distribution of T_eutectic
```

### 17.10 习题（5 个）

**17.1**: Write PyCalphad code for Al-Cu phase diagram.

**17.2**: Implement Scheil-Gulliver and compare with equilibrium.

**17.3**: Use ESPEI to fit a simple binary (1-2 parameters).

**17.4**: Compute carbon activity in austenite (Fe-C, 1000K, x_C=0.02).

**17.5**: Multi-component case: design a duplex stainless steel (50% austenite + 50% ferrite at 1100K).

## 第 18 章 DICTRA — Diffusion Controlled Transformation

### 18.1 Multi-component diffusion theory

**Driving force**: chemical potential gradient.

**Onsager relation**:

$$ J_i = -\sum_j L_{ij} \nabla \mu_j $$

For ideal dilute: 
$$ J_i = -D_i \nabla c_i $$

For multi-component non-ideal:
$$ J_i = -\sum_j D_{ij} \nabla c_j $$

with intrinsic diffusion coefficients $D_{ij}$.

### 18.2 Mobility database

Format like TDB but stores **mobilities M_i**:

$$ M_i^\alpha = M_i^{0,\alpha} \exp\left(\frac{-Q_i^\alpha + RT\ln M_i^{0,\alpha}}{RT}\right) $$

Relate to diffusion via:
$$ D_i = M_i RT $$

**Q_i^α**: activation energy in phase α.

Stored in `*.tdb` with `MQ` parameters.

### 18.3 DICTRA equation (1D)

Multi-component continuity:

$$ \frac{\partial c_i}{\partial t} = \nabla \cdot M_i \nabla \mu_i $$

with $\mu_i$ from CALPHAD G函数.

**Numerical solution**: Finite difference + implicit time stepping.

### 18.4 Carburization simulation

**Setup**: Fe-C blank, carbon source on left.

**Boundary conditions**:
- Left: c_C^surface = c_C^atmosphere (gas C activity)
- Right: zero flux
- Initial: c_C = 0 everywhere

**Code skeleton** (PyCalphad-based, not full DICTRA):

```python
import numpy as np
from pycalphad import calculate

# Parameters
T = 1173  # 900°C
t_total = 3600 * 4  # 4 hours
dt = 60  # 60 s
n_x = 100
dx = 1e-5  # 10 microns

# Domain
x = np.linspace(0, dx*n_x, n_x)

# Carbon profile (start = 0, surface = saturation)
c_C = np.zeros(n_x)
c_C_surface = 0.012  # FCC saturation at 900°C, atom fraction

# Mobility coefficient (approximate)
D_C = 7.8e-12  # m²/s for C in FCC at 900°C

# Time evolution (explicit Euler, simplified)
n_steps = int(t_total / dt)
for step in range(n_steps):
    # Boundary
    c_C[0] = c_C_surface
    
    # Diffusion (Fick approximation)
    c_C[1:-1] += D_C * dt * (c_C[2:] - 2*c_C[1:-1] + c_C[:-2]) / dx**2
    
    # No-flux at right
    c_C[-1] = c_C[-2]

# Plot final profile
import matplotlib.pyplot as plt
plt.plot(x*1e6, c_C)
plt.xlabel('Depth (μm)')
plt.ylabel('C atom fraction')
plt.title(f'Carburization at 900°C for 4 hours')
plt.show()

# Carbon penetration depth
threshold = c_C_surface / 2
penetration_idx = np.where(c_C < threshold)[0][0]
print(f"Case depth (c > 0.5*surface): {x[penetration_idx]*1e6:.1f} μm")
```

### 18.5 Precipitation kinetics — LSW theory

Lifshitz-Slyozov-Wagner for diffusion-controlled coarsening:

$$ \bar{R}^3 - \bar{R}_0^3 = K \cdot t $$

$$ K = \frac{8 \gamma D V_m C_e}{9 RT} $$

- $\bar{R}$: mean radius
- $\gamma$: interface energy
- $D$: diffusion coefficient (matrix)
- $V_m$: molar volume
- $C_e$: equilibrium solubility

**实战**: For γ' in Ni-base superalloy:
- Coarsening rate from MD/DFT γ + DICTRA D
- Predict aging behavior

### 18.6 Welding HAZ simulation

**Cycle**: heat → soak → cool

```python
# Temperature profile (Rosenthal equation for arc welding)
def temperature_profile(x, t, P, v, k, rho_Cp, T_0):
    """Rosenthal solution"""
    r = ...  # distance from arc
    T = T_0 + P/(2*np.pi*k) * np.exp(-v*r / (2*alpha)) / r
    return T

# Apply to local CALPHAD calculation
# Each x has a thermal cycle
# Result: local phase fractions + microstructure
```

### 18.7 习题

**18.1**: Derive Fick's second law from Onsager + chemical potential gradient.

**18.2**: Estimate case depth for Fe-C carburization at 900°C, 4 h.

**18.3**: Use DICTRA (or PyCalphad surrogate) to simulate Cr depletion at grain boundary during sensitization (austenitic stainless steel at 600°C).

**18.4**: LSW coarsening: estimate γ' coarsening rate for typical Ni-base superalloy.

**18.5**: Multi-component diffusion: explain uphill diffusion (counter-intuitive case).

---

