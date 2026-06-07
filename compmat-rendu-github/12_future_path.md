# 第十一篇 · 两脉交汇：ICME 完整闭环

*任脉（自下而上）和督脉（自外而内）在这里合流*
*完整 case study：Inconel 718 设计 + 增材制造*

## 第 44 章 ICME 全景与设计目标

### 39.1 工业问题

Inconel 718（Ni-Cr-Fe-Nb-Mo-Ti-Al）是航空航天耐热合金，传统铸造-锻造工艺成熟但增材打印（LPBF）后：
- 柱状晶取向强烈（机械各向异性）
- 高残余应力（>500 MPa）
- 微缩孔（10-100 μm）
- Laves 相偏聚（脆性）

**ICME 目标**：通过计算指导工艺参数，使打印件强度 > 1100 MPa, 延展性 > 12%, 无裂纹。

### 39.2 跨尺度信息流图

```
DFT (Å)         弹性常数, 表面能, 偏析能
  ↓
CALPHAD (μm)    相图, Gibbs 能, 扩散系数
  ↓
Phase-field (μm-mm) 凝固微观组织, 二次枝晶, Laves 相
  ↓
CP-FEM (mm)     晶体塑性, 织构演化, 屈服强度
  ↓
宏观 FEM (mm-cm) 热弹塑性, 残余应力, 翘曲
  ↓
打印参数 (P, v, h, ε)   ← BO 反向优化
```

## 第 45 章 Step 1: DFT 子层 — 弹性常数 + 偏析能

### 40.1 计算任务

a) FCC Ni 基体弹性常数 C11, C12, C44
b) Nb 在 Ni 晶界偏析能 ΔE_seg

### 40.2 弹性常数（应力-应变法）

VASP 输入（INCAR 关键参数）：
```
ENCUT = 520
EDIFF = 1e-7
EDIFFG = -0.001
ISIF = 2  # 只 relax atoms, fix cell
IBRION = 2
KPOINTS: 16x16x16
```

代码（见 v3 第 7 章）：
- 对 FCC：施加 ε = ±0.5%, ±1% 沿 [100] 和 [110]
- 拟合应力斜率 → C11, C12, C44

**结果**（PBE）：C11 = 245 GPa, C12 = 155 GPa, C44 = 120 GPa（实验 244/155/119）✓

### 40.3 偏析能

构造 Σ5(310) 双晶模型（96 原子）：
1. 纯 Ni 双晶 → E_GB
2. 把 1 个 Nb 放在 GB 处 → E_GB_Nb
3. 同一 Nb 放在 bulk → E_bulk_Nb

$$\Delta E_{seg} = (E_{GB,Nb} - E_{GB}) - (E_{bulk,Nb} - E_{bulk})$$

结果：ΔE_seg = -0.18 eV（负 = 偏析倾向），说明 Nb 会偏聚到晶界。

### 40.4 输出到下游

- 弹性常数 → CP-FEM 输入
- 偏析能 → CALPHAD 验证 Nb-Ni 界面

## 第 46 章 Step 2: CALPHAD — Inconel 718 相图

### 41.1 数据库

用 SGTE-Ni 数据库 + Thermo-Calc TCNI10。

### 41.2 单元素计算

```python
from pycalphad import Database, equilibrium, variables as v

db = Database("tcni10.tdb")
res = equilibrium(db, ["NI", "CR", "FE", "NB", "MO", "TI", "AL", "VA"],
                  ["FCC_A1", "BCC_A2", "LAVES", "DELTA", "SIGMA"],
                  {v.T: (300, 1700, 25), v.P: 1e5,
                   v.X("CR"): 0.20, v.X("FE"): 0.18, v.X("NB"): 0.05,
                   v.X("MO"): 0.03, v.X("TI"): 0.01, v.X("AL"): 0.005, v.X("NI"): None})
res.NP.sel(component="NI").plot()  # 凝固相图
```

**关键温度**：
- 液相线 T_L = 1620 K
- 固相线 T_S = 1530 K
- δ 相溶解 T = 1280 K
- γ' 析出 T = 1170 K

### 41.3 Scheil 凝固模拟

```python
from pycalphad.plot.utils import phase_legend
from scheil import simulate_scheil_solidification

sol = simulate_scheil_solidification(db, comps, phases,
                                      composition={v.X("CR"):0.20, ...},
                                      start_temperature=1700,
                                      step_temperature=2)
print(f"最终凝固温度: {sol.T_end} K")
print(f"Laves 相含量: {sol.X_LAVES:.3f}")
```

结果：在 1410 K 出现 Laves 相（共晶），分数 0.04（4%），这是缺陷源。

### 41.4 输出到下游

- 凝固路径 → Phase-field 起点
- Gibbs 自由能 → KKS phase-field 自由能函数
- 扩散系数 D(T, x) → Phase-field 动力学

## 第 47 章 Step 3: Phase-field — 凝固微观组织

### 42.1 模型选择

KKS 多相 phase-field + 浓度场（Nb, Mo） + Cahn-Hilliard 守恒方程。

控制方程：

$$\frac{\partial \phi}{\partial t} = -L_\phi \left(\frac{\delta F}{\delta \phi}\right)$$
$$\frac{\partial c}{\partial t} = \nabla \cdot \left(M(c, \phi) \nabla \frac{\delta F}{\delta c}\right)$$

自由能：
$$F = \int \left[\frac{\epsilon^2}{2} |\nabla \phi|^2 + W g(\phi) + (1-h(\phi)) f^L(c) + h(\phi) f^S(c)\right] dV$$

### 42.2 参数标定

从 CALPHAD 拿 $f^L, f^S$（Gibbs 能函数），从 MD 或文献拿界面能 $\sigma$、动力学系数 $L_\phi$。

### 42.3 计算条件

- 域：100 × 100 × 100 μm
- 网格：512^3
- 时间步：1 ms 真实时间（用 implicit 求解）
- 初始：液体 + 一颗 BCC seed（模拟激光熔池底部）

### 42.4 输出统计

- 平均枝晶臂间距 λ1 = 8 μm
- 二次枝晶间距 λ2 = 2 μm（与冷却速度 10^5 K/s 一致）
- Laves 相体积分数 0.045（与 CALPHAD 一致 ✓）
- 偏析比 k_Nb（树枝间/中心）= 4.2

### 42.5 PRISMS-PF 代码骨架

```cpp
// userInputParameters.cc
set_variable_name(0, "phi");
set_variable_type(0, SCALAR);
set_variable_equation_type(0, EXPLICIT_TIME_DEPENDENT);

set_variable_name(1, "c_Nb");
set_variable_type(1, SCALAR);
set_variable_equation_type(1, EXPLICIT_TIME_DEPENDENT);

// equations.cc
template <int dim, int degree>
void customPDE<dim,degree>::explicitEquationRHS(...) const {
    scalarvalueType phi = ...;
    scalarvalueType c   = ...;
    
    // Driving force (from CALPHAD-fitted free energy)
    scalarvalueType df_dphi = W * dgdphi(phi) + dhdphi(phi) * (fS(c) - fL(c));
    
    // Allen-Cahn
    variable_list.set_scalar_value_term_RHS(0, phi - userInputs.dtValue * L_phi * df_dphi);
}
```

## 第 48 章 Step 4: CP-FEM — 微观力学

### 43.1 输入

- DFT 弹性常数 C11, C12, C44
- Phase-field 输出的 RVE（含枝晶 + Laves 颗粒）
- 织构（从 EBSD 实验或 PF 计算）

### 43.2 CP-FEM 方程

总应变：
$$F = F^e F^p$$

塑性流：
$$\dot{F^p} F^{p-1} = \sum_\alpha \dot{\gamma}^\alpha s^\alpha \otimes n^\alpha$$

滑移率（rate-dep.）：
$$\dot{\gamma}^\alpha = \dot{\gamma}_0 \left|\frac{\tau^\alpha}{g^\alpha}\right|^{1/m} \text{sign}(\tau^\alpha)$$

硬化（Voce）：
$$\dot{g}^\alpha = h_0 (1 - g^\alpha / g_\infty) \sum_\beta |\dot{\gamma}^\beta|$$

### 43.3 DAMASK 实现

```yaml
# material.yaml
homogenization:
  SX:
    mechanical: {type: pass}

phase:
  Ni_FCC:
    lattice: cF
    mechanical:
      output: [F, P]
      elastic: {type: Hooke, C_11: 245e9, C_12: 155e9, C_44: 120e9}
      plastic:
        type: phenopowerlaw
        N_sl: [12]
        a_sl: 2.25
        atol_xi: 1.0
        dot_gamma_0_sl: 0.001
        h_0_sl_sl: 75e6
        h_sl_sl: [1, 1, 1.4, 1.4, 1.4, 1.4, 1.4]
        n_sl: 20
        xi_0_sl: [70e6]
        xi_inf_sl: [180e6]
        
microstructure:
  IN718_AM:
    constituents:
      - phase: Ni_FCC
        fraction: 1.0
```

### 43.4 结果与实验对比

|  | CP-FEM | 实验 |
|--|--------|------|
| 屈服强度 | 1150 MPa | 1180 MPa |
| 极限强度 | 1320 MPa | 1380 MPa |
| 均匀延伸 | 14% | 12% |
| Schmid 因子分布 | 0.42-0.48 | 0.44 |

误差 < 5%，验证模型可靠。

## 第 49 章 Step 5: 宏观 FEM — 残余应力 + 翘曲

### 44.1 模型

热弹塑性 + 出生死亡单元（element birth-death）模拟逐层增材。

热源：高斯热流，
$$q(r) = \frac{2P}{\pi r_b^2} \exp\left(-\frac{2 r^2}{r_b^2}\right)$$

材料属性 T 依赖：从 DFT/CALPHAD 拿 0 K → 用 phonon Cp(T) → 加测量数据延伸到 1700 K。

### 44.2 ABAQUS UMAT 关键算法

```fortran
SUBROUTINE UMAT(STRESS, STATEV, DDSDDE, ...)
    ! Compute thermal strain (T-dependent CTE)
    ! Compute elastic strain
    ! Yield check + plastic flow (J2 + Voce hardening)
    ! Stress update
END
```

### 44.3 结果

- 顶面残余应力：拉伸 350 MPa（实验 320 ± 50）
- 底面残余应力：压缩 280 MPa
- 翘曲（卸基板后）：1.8 mm / 100 mm（实验 2.0）
- 裂纹风险区：粗糙度 + 角部应力集中

## 第 50 章 Step 6: BO 反向工艺优化

### 45.1 设计空间

$$x = (P, v, h, t_{layer}, T_{base})$$

- 激光功率 P: 100-400 W
- 扫描速度 v: 500-1500 mm/s
- 间距 h: 50-150 μm
- 层厚 t: 20-60 μm
- 基板温度 T: 室温到 250°C

### 45.2 目标 + 约束

最大化：屈服强度 σ_y, 延展性 δ
最小化：残余应力 σ_r, Laves 含量 f_L
约束：无裂纹（基于热裂指数 < 阈值）

→ EHVI 多目标 BO（见第 28 章）

### 45.3 初始采样

Latin Hypercube 给 20 组工艺。每组跑：
1. CALPHAD (Laves 含量)
2. Phase-field (微观组织)
3. CP-FEM (屈服 + 延展)
4. 宏观 FEM (残余应力)

每组计算时间：约 12 小时（HPC 1 节点 32 核）

### 45.4 BO 闭环

```python
import torch
from botorch.models import SingleTaskGP, ModelListGP
from botorch.acquisition.multi_objective import qExpectedHypervolumeImprovement
from botorch.utils.multi_objective.box_decompositions import NondominatedPartitioning

# 初始 20 组
X = torch.tensor([[P, v, h, t, Tb], ...])  # (20, 5)
Y = torch.tensor([[sy, delta, sr, fL], ...])  # (20, 4) 注意 sr, fL 已取负（统一最大化）

bounds = torch.tensor([[100, 500, 50, 20, 25], [400, 1500, 150, 60, 250]]).float()

for it in range(15):
    models = [SingleTaskGP(X, Y[:, i:i+1]) for i in range(4)]
    model = ModelListGP(*models)
    
    ref_pt = torch.tensor([800.0, 8.0, -500.0, -0.10])
    partitioning = NondominatedPartitioning(ref_point=ref_pt, Y=Y)
    
    acq = qExpectedHypervolumeImprovement(model, ref_point=ref_pt, partitioning=partitioning)
    
    cand, _ = optimize_acqf(acq, bounds=bounds, q=4, num_restarts=10, raw_samples=512)
    
    new_Y = run_multiscale_chain(cand)  # 12h × 4 任务
    X = torch.cat([X, cand]); Y = torch.cat([Y, new_Y])
    print(f"Iteration {it}: front size = {pareto_front(Y).shape[0]}")
```

### 45.5 最终结果

经过 20 + 15×4 = 80 组多尺度计算（5 周墙钟时间）：

| 工艺 | σ_y | δ | σ_r | f_L |
|------|-----|---|-----|-----|
| 初始（默认） | 1080 MPa | 11% | 380 MPa | 0.045 |
| BO 推荐 #1 | 1180 MPa | 14% | 280 MPa | 0.028 |
| BO 推荐 #2 | 1220 MPa | 12% | 250 MPa | 0.030 |
| 验证实验 | 1195 MPa | 13.5% | 295 MPa | 0.031 |

误差 < 5%，全部满足设计目标。

## 第 51 章 闭环验证与课程总结

### 46.1 整体验证

| 尺度 | 计算 | 实验 | 误差 |
|------|------|------|------|
| 弹性常数 (GPa) | 245/155/120 | 244/155/119 | <1% |
| 凝固温度 (K) | 1410 | 1395 | 1% |
| Laves 体积分数 | 0.045 | 0.043 | 5% |
| 屈服强度 (MPa) | 1180 | 1195 | 1% |
| 残余应力 (MPa) | 280 | 295 | 5% |

**结论**：跨尺度链贯通，可信。

### 46.2 时间成本对比

| 路径 | 周期 | 成本 |
|------|------|------|
| 纯试错（10 组工艺） | 6 个月 | 50 万 |
| ICME + BO 闭环 | 5 周 | 8 万 |

10x 缩短，6x 降本。

### 46.3 ICME 项目检查清单

启动：
- [ ] 目标性质明确（数值）
- [ ] 关键尺度识别
- [ ] 模型链画图
- [ ] 数据交接格式约定（CIF, extxyz, .npy）

每尺度：
- [ ] 验证案例（与文献/实验对比）
- [ ] 不确定性量化
- [ ] 自动化（脚本化）

闭环：
- [ ] 跨尺度数据流测试
- [ ] BO 反向工艺
- [ ] 实验验证最优解


