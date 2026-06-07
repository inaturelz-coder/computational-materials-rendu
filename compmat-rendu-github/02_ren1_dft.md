# 第六篇 · 任脉第 5 步：宏观层 — CP-FEM

*上游：Phase-field 提供微观组织；CALPHAD 提供相成分；DFT 提供弹性常数*
*下游：工程性能 — 寿命、断裂、疲劳。任脉到此到顶*

*任脉打通：你能从 DFT 算到 CP-FEM。下面进入督脉*


## 第 24 章 连续介质力学回顾

### 19.1 应变度量

变形梯度 F：
$$F_{ij} = \frac{\partial x_i}{\partial X_j}$$

右 Cauchy-Green 张量：$C = F^T F$
左 Cauchy-Green 张量：$B = F F^T$
Green-Lagrange 应变：$E = \frac{1}{2}(C - I)$
对数应变（true strain）：$\varepsilon^{\log} = \frac{1}{2} \ln C$

**小应变近似**：$\varepsilon = \frac{1}{2}(\nabla u + \nabla u^T)$

### 19.2 应力度量

Cauchy 应力 σ（真应力）：作用在变形后构型
第一 PK 应力 P：$P = J \sigma F^{-T}$，作用在参考构型
第二 PK 应力 S：$S = F^{-1} P$，对称

### 19.3 弹塑性分解

变形梯度乘法分解：
$$F = F^e F^p$$

塑性变形梯度 $F^p$ 是塑性流引起的，不含旋转。

塑性流率：
$$L^p = \dot{F^p} (F^p)^{-1} = \sum_\alpha \dot{\gamma}^\alpha s_0^\alpha \otimes n_0^\alpha$$

其中 $s_0^\alpha, n_0^\alpha$ 是参考构型滑移方向和法向（晶体学定义）。

## 第 25 章 晶体塑性本构

### 20.1 滑移系统

FCC 12 个滑移系：4 个 {111} 面 × 3 个 ⟨110⟩ 方向
BCC 12 + 12 + 24 = 48 个滑移系（{110}, {112}, {123}）
HCP 基面 + 棱柱面 + 锥面，共 18 个

### 20.2 滑移率本构（rate-dependent）

经典 phenopowerlaw（DAMASK 默认）：

$$\dot{\gamma}^\alpha = \dot{\gamma}_0 \left|\frac{\tau^\alpha}{g^\alpha}\right|^n \text{sign}(\tau^\alpha)$$

- $\dot{\gamma}_0$：参考剪切率（如 10^-3 s^-1）
- $n$：率敏感参数（金属常温 ~20，高温降至 ~5）
- $\tau^\alpha = s^\alpha \cdot \sigma \cdot n^\alpha$：解析剪应力
- $g^\alpha$：滑移阻力（硬化变量）

### 20.3 硬化模型对比

**A. Voce 硬化**：
$$\dot{g}^\alpha = h_0 \left(1 - \frac{g^\alpha}{g_\infty}\right)^a \sum_\beta h_{\alpha\beta} |\dot{\gamma}^\beta|$$

简单，参数少（4 个：$h_0, g_\infty, g_0, a$），适合大变形。

**B. 位错密度模型（Mecking-Kocks）**：
$$\dot{\rho}^\alpha = k_1 \sqrt{\sum_\beta \rho^\beta} - k_2 \rho^\alpha \dot{\gamma}^\alpha$$

$$g^\alpha = \mu b \sqrt{\sum_\beta h_{\alpha\beta} \rho^\beta}$$

物理意义清晰，但参数多。适合疲劳、温度依赖。

**C. 应变梯度塑性**：加入 GND（geometrically necessary dislocation）
$$\rho^G_\alpha = \frac{1}{b} |\nabla \gamma^\alpha|$$

捕获尺度效应（small-is-stronger）。

### 20.4 隐式积分

CP-FEM 关键难点：本构积分是高度非线性。每个增量需要 Newton-Raphson 迭代：

```
Given: F_{n+1}, F_n, F^p_n, g_n
Guess: F^p_{n+1} = F^p_n
Loop:
  1. F^e_{n+1} = F_{n+1} (F^p_{n+1})^-1
  2. σ_{n+1} = elastic_response(F^e)
  3. For each α: compute τ^α, dot_γ^α
  4. R = F^p_{n+1} - F^p_n - Δt Σ dot_γ^α s⊗n F^p_n
  5. If |R| < tol: break
  6. Newton update: F^p ← F^p - (∂R/∂F^p)^-1 R
return F^p_{n+1}, g_{n+1}
```

### 20.5 织构与极图

每个积分点存 Euler 角 (φ1, Φ, φ2)，整体集合 = ODF（取向分布函数）。

```python
import numpy as np
import matplotlib.pyplot as plt
from orix.crystal_map import CrystalMap
from orix.quaternion import Orientation, symmetry

# 假设 CP-FEM 输出 N 个晶粒最终 Euler 角
eulers = np.loadtxt("eulers_final.txt")  # (N, 3)
ori = Orientation.from_euler(eulers, symmetry=symmetry.Oh)

# 画 {111} 极图
ori.scatter(projection="stereographic", direction=[1,1,1])

# 算织构强度（J index）
def texture_index(eulers, nbins=18):
    f, _ = np.histogramdd(eulers, bins=nbins)
    f_unit = 1.0 / (nbins**3)
    return np.sum((f/eulers.shape[0] - f_unit)**2)
print(f"J = {texture_index(eulers):.4f}")  # 0 = 随机, ↑ 织构强
```

## 第 26 章 DAMASK 实战完整工程

### 21.1 DAMASK 文件结构

```
mat.yaml          # 材料/相/微观组织
geom.vti          # 几何 (Voxel)
load.yaml         # 边界条件 + 加载路径
numerics.yaml     # 数值参数（步长、tol）
```

### 21.2 完整 mat.yaml（铜单晶拉伸）

```yaml
homogenization:
  SX: {N_constituents: 1, mechanical: {type: pass}}

phase:
  Cu:
    lattice: cF
    mechanical:
      output: [F, P, F_e, F_p, O]
      elastic:
        type: Hooke
        C_11: 168.4e9
        C_12: 121.4e9
        C_44: 75.4e9
      plastic:
        type: phenopowerlaw
        output: [xi_sl, gamma_sl]
        N_sl: [12]
        n_sl: 20
        a_sl: 2.25
        h_0_sl-sl: 75e6
        h_sl-sl: [1, 1, 1.4, 1.4, 1.4, 1.4, 1.4]
        xi_0_sl: [31e6]
        xi_inf_sl: [63e6]
        dot_gamma_0_sl: 0.001

material:
  - homogenization: SX
    constituents:
      - phase: Cu
        v: 1.0
        O: [1.0, 0.0, 0.0, 0.0]  # 取向 quaternion
```

### 21.3 load.yaml（单轴拉伸到 30%）

```yaml
solver:
  mechanical: spectral_basic

loadstep:
  - boundary_conditions:
      mechanical:
        dot_F: [[1.0e-3, 0, 0],
                [0, x, 0],
                [0, 0, x]]
        P:     [[x, x, x],
                [x, 0, x],
                [x, x, 0]]
    discretization:
      t: 300
      N: 100
    f_out: 10
```

`x` = unknown（自动求解），保证 P22=P33=0（自由侧面）。

### 21.4 后处理

```bash
# 转 HDF5 → VTK
DAMASK_grid --geom geom.vti --load load.yaml --material mat.yaml
DAMASK_grid postResults --integrationPoints

# Python: 提取 σ-ε 曲线
python -c "
import damask
result = damask.Result('cu_load.hdf5')
result.add_stress_Cauchy()
result.add_strain('F', 'V', 'ln')
sigma = result.get('sigma'); eps = result.get('epsilon_V^0.0(F)')
import numpy as np
np.savetxt('curve.dat', np.column_stack([eps[:,0,0], sigma[:,0,0]/1e6]))
"
```

### 21.5 RVE 生成 — 从 EBSD 到 CP-FEM

```python
import numpy as np
from dream3d.workflow import build_synthetic_microstructure

# 输入 EBSD 数据 → 重建 RVE
ebsd = dream3d.read_ang("scan.ang")
stats = ebsd.compute_stats()  # 晶粒尺寸分布, 织构

# 生成同分布合成 RVE
rve = build_synthetic_microstructure(
    size=(64, 64, 64),
    grain_size_dist=stats.size,
    ODF=stats.ODF,
    phase="FCC"
)
rve.to_damask("geom.vti", "material.yaml")
```

## 第 27 章 全场 vs 平均场

### 22.1 平均场方法

**自洽（Self-consistent, Hill 1965）**：每晶粒嵌入"等效介质"
**Taylor**：所有晶粒等应变（上界，过硬）
**Sachs**：所有晶粒等应力（下界，过软）
**VPSC（Visco-Plastic Self-Consistent, Lebensohn）**：黏塑性自洽，工业广泛用

```
优点: 快 (几秒-分钟), 适合工艺优化
缺点: 不给局部场 (热点、起裂位置)
```

### 22.2 全场方法

**有限元 CP-FEM（DAMASK FE, MOOSE）**：通用，可处理任意几何
**FFT 谱方法 CP-FEM（DAMASK grid, MASSIF）**：周期 RVE 极快（比 FEM 快 10-100×）

```
优点: 局部场, 热点
缺点: 慢, 需要 RVE 生成
```

### 22.3 决策树

| 任务 | 推荐方法 |
|------|----------|
| 工艺优化（轧制路径） | VPSC |
| 织构演化 | VPSC 或 FFT |
| 起裂位置预测 | FFT 或 FEM |
| 复杂几何（涡轮叶片） | FEM |
| 大变形（>50%） | FEM |
| 疲劳热点 | FFT |

---



# 督 脉 · 自外而内 · 数据驱动闭环 / Du-meridian — Data-driven loop (Top-down)

*督脉的逻辑：物理建模慢，数据驱动快。四个阶段：表征数据 → ML 建模 → BO 决策 → UQ 量化*

*你正在进入督脉第 2 阶段：ML for Materials（第 1 阶段"表征"放在第十篇）*
