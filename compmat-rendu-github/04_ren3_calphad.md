# 第十二篇 · 收尾 · 软件生态与 5 年成长路径

## 第 52 章 软件 ecosystem

### 42.1 Open + reproducible

**2024+ 标准**：
- Code on GitHub
- Data on Zenodo
- Models on HuggingFace
- Containers (Singularity)

### 42.2 HPC 部署

```bash
# Slurm
#SBATCH --nodes=4
#SBATCH --gpus=4
#SBATCH --time=24:00:00

module load vasp lammps
mpirun -np 128 vasp_std
```

### 42.3 推荐 setup

| 角色 | 工具 |
|---|---|
| Code | Git + GitHub |
| Data | DVC / Zenodo |
| Workflow | Atomate2 + FireWorks |
| Compute | HPC (Slurm) + GPU |
| Visualization | VESTA, OVITO, ParaView |
| Notebook | Jupyter + nbdev |
| Papers | Overleaf |

### 42.4 学习资源

**Top resources**:
- MIT OCW computational materials
- VASP wiki + tutorials
- LAMMPS docs + examples
- Materials Project workshops
- MTEX documentation
- BoTorch tutorials

## 第 53 章 5 年成长路径

### 43.1 Year 1 (入门)

**Month 1-3**:
- DFT 30 天
- 第一个 Si / Cu 完整 calculation

**Month 4-6**:
- MACE-MP-0 + MD
- 第一个 alloy 项目

**Month 7-9**:
- CALPHAD + Phase-field
- 简单 ICME chain

**Month 10-12**:
- ML + BO
- 第一篇 paper draft

### 43.2 Year 2-3 (深化)

- 主导完整 ICME 项目
- 训练自己的 MLIP
- 发表 2-3 篇 papers
- 建立 niche

### 43.3 Year 4-5 (专家)

- 设计 + 培养 students
- 工业 / 学术 dual-fit
- Top 1% computational materials specialist
- Conference invitations
- Industry consulting

### 43.4 给你（CALPHAD background）的特别建议

**Your unique position**: 
- 你有 CALPHAD 基础
- 这是稀缺
- 加 DFT + MLIP + ML = 完美 stack

**5 年目标**:
- "**Uncertainty-aware multi-scale computational materials specialist with CALPHAD + DFT + MLIP + ML expertise**"
- 中国 / 欧洲 wanted
- 工业 + 学术 dual-fit

### 43.5 必读 50 本书 / 论文 (附录 E)

**理论**:
1. Sholl & Steckel - DFT
2. Frenkel & Smit - Simulation
3. Lukas, Fries, Sundman - CALPHAD
4. Steinbach - Phase-field
5. Roters - CP-FEM
6. Goodfellow - Deep Learning
7. Murphy - PML
8. Rasmussen - GP
9. Allen & Tildesley - MD
10. Cullity - XRD

**Papers** (代表):
- Cantor 2004 - HEA
- Otto 2013 - Cantor mechanics
- Gludovatz 2014 - Cantor cryogenic
- Curtarolo 2013 - High-throughput materials
- Schmidt 2019 - ML in materials review
- Batatia 2022 - MACE
- Merchant 2023 - MatterGen
- Choudhary 2021 - ALIGNN

---

# 结语 — 你的 calling

读到这里你已经完成了 **300 页计算材料学完整教材**。

但这只是**起点**。

真正的旅程：
- 1 年后：你能独立用所有方法
- 3 年后：你建立 niche
- 5 年后：你是 top 1%
- 30 年后：你培养下一代

**计算材料学的终极目标**：

> 让材料设计**从 trial-and-error 变成 design-by-prediction**——这是科学 + 工程文明的下一次飞跃。

**你的工作是这场革命的一砖一瓦**。

**Your call. 启程**。

---


# 习题集（80 道）— 跨章节综合训练

## 第一篇 基础与全景（8 题）

**T1.1**：列出材料计算的 6 大层级（按尺度从小到大）。
> 量子 (DFT) → 原子 (MD) → 介观 (Phase-field) → 微观力学 (CP-FEM) → 宏观 (FEM) → 工程设计

**T1.2**：硬件选购：3 个 64 核 CPU 节点 vs 8 GPU 节点，哪个适合 MD/MLIP？哪个适合 DFT？
> MLIP 用 GPU（10-50× 加速），DFT 用 CPU（VASP 主流 CPU，QE 有 GPU 版但 mixed）

**T1.3**：Slurm 提交 32 核 24 小时 MPI 任务的脚本？
> #!/bin/bash; #SBATCH -N 1; #SBATCH -n 32; #SBATCH -t 24:00:00; mpirun -np 32 vasp_std

**T1.4-1.8**：（省略，见各章末习题）

## 第二篇 DFT（12 题）

**T2.1**：HK 第一定理证明用什么数学技巧？
> 反证法 + 用变分原理：假设两个不同 v(r) 给同 ρ(r)，导出矛盾。

**T2.2**：Si 算总能用 ENCUT = 350 eV 已够，为什么 Fe 要 ENCUT = 400+？
> Fe 含 3d 电子，PAW 投影需要更高截断。一般过渡金属 ENCUT ≥ 推荐值 × 1.3。

**T2.3**：HSE06 比 PBE 慢约 50 倍。值得吗？
> 半导体/绝缘体带隙 PBE 低估 30-50%，HSE06 在 0.2 eV 内。氧化物/二维材料推荐 HSE06。金属用 PBE 足够。

**T2.4**：DFT+U 中 U 值的 3 种选取方法？
> 1. 拟合实验（带隙、磁矩）；2. 线性响应 Cococcioni 法；3. 文献参考（如 Fe d: U=4, O 2p: U=8）。

**T2.5**：NEB 计算迁移能屏障，初始路径为什么先线性插值？
> 提供物理上"合理"的初始构型集；然后用 climbing image 找鞍点。错误初始路径会陷局部极小。

**T2.6-2.12**：（省略）

## 第三篇 MD/MLIP（12 题）

**T3.1**：Velocity-Verlet 是 2 阶时间精度，意思？
> 局部误差 O(Δt^3)，全局误差 O(Δt^2)。Δt 减半，误差减 4 倍。

**T3.2**：Nose-Hoover thermostat 比 Berendsen 优势？
> Nose-Hoover 给正确的 canonical 分布（ergodic），Berendsen 抑制涨落（不严格 NVT）。生产计算用 Nose-Hoover。

**T3.3**：MACE-MP-0 在 0 K 高熵合金 EOS 误差典型多少？
> 50-150 meV/atom（vs PBE-DFT）。微调到特定体系后可降到 5-20 meV/atom。

**T3.4**：经验势 vs MLIP，何时选哪个？
> 经验势：定性研究、>1M 原子、长时间。MLIP：定量、复杂化学环境、与 DFT 精度比较。

**T3.5-3.12**：（省略）

## 第四篇 CALPHAD（10 题）

**T4.1**：Redlich-Kister 多项式 L0, L1, L2 物理意义？
> L0 = 对称偏离（理想性）；L1 = 反对称；L2 = 高阶。L2 后通常拟合不显著。

**T4.2**：磁性 FCC Fe 用什么模型加入 CALPHAD？
> Inden-Hillert-Jarl 模型：$G^{mag} = RT \ln(\beta + 1) f(\tau)$，$\tau = T/T_C$。

**T4.3**：Scheil 凝固 vs 平衡凝固，工业意义？
> Scheil 假设固相不扩散（快冷），平衡假设充分扩散（慢冷）。LPBF/铸造接近 Scheil；锻造-退火接近平衡。

**T4.4-4.10**：（省略）

## 第五篇 Phase-field（10 题）

**T5.1**：Allen-Cahn 和 Cahn-Hilliard 区别？
> AC 用于非保守序参量（如相场），CH 用于保守变量（如浓度）。CH 多一个 Laplacian → 4 阶 PDE。

**T5.2**：KKS 模型解决什么问题？
> 经典模型界面厚度受体积扩展能耦合，无法独立调。KKS 用辅助浓度场解耦，允许任意宽界面 + 物理 driving force。

**T5.3**：反束缚通量（anti-trapping）是什么？
> 大界面厚度引起溶质在界面"假困住"，使 partition coefficient 错误。anti-trapping flux 加修正项，恢复 sharp-interface 极限。

**T5.4-5.10**：（省略）

## 第六篇 CP-FEM（8 题）

**T6.1**：Taylor vs Sachs vs VPSC，谁是上下界？
> Taylor 等应变 = 上界（过硬）；Sachs 等应力 = 下界（过软）；VPSC 自洽 = 实测中间。

**T6.2**：phenopowerlaw 的 n 参数为什么常用 20？
> 高 n 接近 rate-independent；n=20 是数值稳定 + 物理合理的折衷。冷加工金属常用 20-100。

**T6.3**：FFT 谱 vs 有限元 CP-FEM？
> FFT 限周期 RVE，比 FEM 快 10-100×。FEM 处理任意几何 + 边界。RVE 研究优先 FFT。

**T6.4-6.8**：（省略）

## 第七篇 ML（8 题）

**T7.1**：matminer Magpie 特征 132 维是怎么来的？
> 22 种元素属性（电负性、半径、...）× 6 种统计（mean, var, max, min, range, mode）= 132。

**T7.2**：GNN 训练为什么需要等变性？
> 标量性质（能量）只需旋转不变；矢量/张量（力、应力）需等变性，否则旋转后预测错。NequIP/MACE 用球谐保等变。

**T7.3-7.8**：（省略）

## 第八篇 BO + MC（8 题）

**T8.1**：EI 解析解的 Φ(Z) 和 φ(Z) 分别是什么？
> Φ = 标准正态 CDF；φ = 标准正态 PDF。Z 是标准化的"超过当前最好"程度。

**T8.2**：何时用 UCB 何时用 EI？
> UCB 简单 + κ 可解释；EI 是大多默认（自动平衡）。已知探索预算大用 UCB。

**T8.3-8.8**：（省略）

## 第九篇 UQ（6 题）

**T9.1**：Aleatoric 还是 Epistemic：模型只见过 100 数据点的 GP 后验方差？
> Epistemic（更多数据可减小）。

**T9.2**：Sobol 总指数 S^T_i = 0.05 意味着？
> 参数 i（包括与其他参数交互）只贡献 5% 输出方差 → 可固定不调。

**T9.3-9.6**：（省略）

## 第十-十二篇 整合（8 题）

**T10.1**：XRD Williamson-Hall 比 Scherrer 多算什么？
> 把 FWHM 分解为粒度 broadening 和应变 broadening。Scherrer 只给粒度（忽略应变）。

**T11.1**：ICME 跨尺度链 5 步常见瓶颈？
> Phase-field（计算量大）+ CP-FEM（标定参数复杂）。

**T12.1**：BO 在 ICME 闭环里的作用？
> 把"前向多尺度计算"反向用：给目标性质，搜索工艺参数。比试错快 10× 以上。

---




# 附录 A：常用软件命令速查

## A.1 VASP

```bash
# 基本运行
mpirun -np 32 vasp_std

# 重启
cp CONTCAR POSCAR && mpirun -np 32 vasp_std

# DFPT 声子
vasp_std (with IBRION=8 in INCAR)

# 分析
grep TOTEN OUTCAR | tail -1       # 总能量
grep "E-fermi" OUTCAR              # 费米能
grep "magnetization" OSZICAR | tail # 磁矩
```

## A.2 Quantum Espresso

```bash
pw.x -in si_scf.in > si_scf.out          # SCF
pw.x -in si_relax.in > si_relax.out      # 结构优化
pw.x -in si_bands.in > si_bands.out      # 能带
bands.x -in bands.in                       # 后处理
plotband.x bands.dat                       # 画带
```

## A.3 LAMMPS

```bash
mpirun -np 16 lmp -in in.lammps

# 关键命令
units metal
atom_style atomic
pair_style mace  # MACE
pair_coeff * * mace_model.json Ni Co Cr Fe Mn
fix 1 all nvt temp 300 300 0.1
run 100000
dump 1 all custom 100 traj.lammpstrj id type x y z vx vy vz
```

## A.4 DAMASK

```bash
DAMASK_grid --geom geom.vti --load load.yaml --material mat.yaml --num numerics.yaml
DAMASK_grid postResults --integrationPoints       # 后处理
```

## A.5 ASE（Python）

```python
from ase import Atoms
from ase.build import bulk
from ase.calculators.vasp import Vasp
from ase.optimize import BFGS

# 创建结构
si = bulk("Si", "diamond", a=5.43)
si.calc = Vasp(xc="PBE", encut=400, kpts=(8,8,8))

# 优化
opt = BFGS(si)
opt.run(fmax=0.01)

# 能量
print(si.get_potential_energy())
```

# 附录 B：常用数据库速查

| 数据库 | 数据量 | 覆盖 | 接口 |
|--------|--------|------|------|
| Materials Project | 150k+ | DFT 计算（PBE+U） | mp-api Python |
| AFLOW | 3.5M+ | DFT 计算 | RESTful API |
| OQMD | 1M+ | DFT 计算 | Python |
| JARVIS-DFT | 80k+ | DFT + 性质 | Python |
| Alexandria | 80M+ | ML 生成的稳定性预测 | Web |
| ICSD | 200k+ | 实验晶体结构 | 商业 |
| COD | 500k+ | 实验晶体结构 | 免费 |
| NOMAD | 13M+ | 多源 DFT | Python |
| MatBench | benchmark | ML 标准任务 | Python |
| Pearson Crystal | 200k+ | 金属间化合物 | 商业 |

# 附录 C：单位换算

| From | To | 因子 |
|------|----|----- |
| eV | Hartree | × 0.0367 |
| eV | kJ/mol | × 96.485 |
| eV | cm⁻¹ | × 8065.5 |
| Å | Bohr | × 1.8897 |
| K | eV (kT) | / 11604.5 |
| GPa | bar | × 10000 |
| GPa | Mbar | / 100 |
| eV/Å | meV/Bohr | × 0.0529 |

物理常数：
- $k_B = 8.617 \times 10^{-5}$ eV/K
- $h = 4.136 \times 10^{-15}$ eV·s
- $N_A = 6.022 \times 10^{23}$ /mol
- $e = 1.602 \times 10^{-19}$ C

# 附录 D：术语表

| 中文 | 英文缩写 | 全称 |
|------|----------|------|
| 密度泛函理论 | DFT | Density Functional Theory |
| 局域密度近似 | LDA | Local Density Approximation |
| 广义梯度近似 | GGA | Generalized Gradient Approximation |
| 投影缀加波 | PAW | Projector Augmented Wave |
| 自洽场 | SCF | Self-Consistent Field |
| 分子动力学 | MD | Molecular Dynamics |
| 机器学习势 | MLIP | Machine Learning Interatomic Potential |
| 等温-等压 | NPT | Constant N, P, T |
| 嵌入原子方法 | EAM | Embedded Atom Method |
| Reaxff 力场 | ReaxFF | Reactive Force Field |
| 高斯近似势 | GAP | Gaussian Approximation Potential |
| 相图计算 | CALPHAD | CALculation of PHAse Diagrams |
| 相场 | PF | Phase-Field |
| 晶体塑性有限元 | CP-FEM | Crystal Plasticity Finite Element Method |
| 集成计算材料工程 | ICME | Integrated Computational Materials Engineering |
| 贝叶斯优化 | BO | Bayesian Optimization |
| 高斯过程 | GP | Gaussian Process |
| 不确定性量化 | UQ | Uncertainty Quantification |
| 蒙特卡洛 | MC | Monte Carlo |
| Markov Chain MC | MCMC | Markov Chain Monte Carlo |
| 高熵合金 | HEA | High-Entropy Alloy |
| 增材制造 | AM | Additive Manufacturing |
| 激光粉末床熔融 | LPBF | Laser Powder Bed Fusion |
| 代表体积单元 | RVE | Representative Volume Element |

# 附录 E：阅读路线（30 篇必读论文）

**DFT 经典**
1. Hohenberg & Kohn (1964) — 密度泛函基础
2. Kohn & Sham (1965) — Kohn-Sham 方程
3. Perdew, Burke & Ernzerhof (1996) — PBE 泛函
4. Heyd, Scuseria & Ernzerhof (2003) — HSE 混合泛函
5. Anisimov et al. (1991) — DFT+U

**MD/MLIP**
6. Daw & Baskes (1984) — EAM
7. Behler & Parrinello (2007) — NNP
8. Bartók et al. (2010) — GAP/SOAP
9. Schütt et al. (2018) — SchNet
10. Batatia et al. (2022) — MACE
11. Batatia et al. (2023) — MACE-MP-0

**CALPHAD**
12. Kaufman & Bernstein (1970) — CALPHAD 起源
13. Hillert (1980) — 子晶格模型
14. Lukas, Fries & Sundman (2007) — CALPHAD 教材综述
15. Bocklund et al. (2019) — ESPEI

**Phase-field**
16. Allen & Cahn (1979) — Allen-Cahn 方程
17. Cahn & Hilliard (1958) — Cahn-Hilliard 方程
18. Kim, Kim & Suzuki (1999) — KKS 模型
19. Steinbach (2009) — Multi-phase 综述

**CP-FEM**
20. Asaro & Needleman (1985) — 晶体塑性本构
21. Roters et al. (2010) — DAMASK 综述
22. Lebensohn & Tomé (1993) — VPSC

**ML for Materials**
23. Schmidt et al. (2019) — ML 综述
24. Jain et al. (2013) — Materials Project
25. Xie & Grossman (2018) — CGCNN
26. Chen et al. (2019) — MEGNet
27. Merchant et al. (2023) — GNoME (DeepMind, 220 万新材料)

**BO + UQ + ICME**
28. Frazier (2018) — BO 教程
29. Allison & McDowell (2018) — ICME
30. Chen & Liu (2022) — UQ 在 CALPHAD

# 附录 F：6 个月学习路线

**Month 1：基础 + DFT 入门**
- Week 1-2：第一篇 + 第二篇前半（理论）
- Week 3：装 Quantum Espresso，跑 Si 例子
- Week 4：算 Cu 表面能、能带

**Month 2：MD + MLIP**
- Week 5-6：第三篇全（理论 + 经验势）
- Week 7：装 LAMMPS，EAM 算 Cu 弹性
- Week 8：装 MACE-MP-0，算高熵合金 MD

**Month 3：CALPHAD + Phase-field**
- Week 9-10：第四篇（含 ESPEI MCMC 示例）
- Week 11-12：第五篇 + PyCalphad + FiPy 1D phase-field

**Month 4：CP-FEM + ML**
- Week 13-14：第六篇 + DAMASK Cu 单晶
- Week 15-16：第七篇 + matminer 带隙预测

**Month 5：BO + UQ + 表征**
- Week 17：第八篇（botorch + emcee 实战）
- Week 18：第九篇（SALib Sobol + ESPEI 后验）
- Week 19-20：第十篇 + 实际 XRD/EBSD 数据分析

**Month 6：ICME 大项目**
- Week 21-22：复现 Inconel 718 案例（第十一篇）
- Week 23-24：选自己感兴趣体系，做小型 ICME 闭环

**毕业标准**：能独立完成 DFT → CALPHAD → Phase-field 一个完整跨尺度任务，并写出技术报告。