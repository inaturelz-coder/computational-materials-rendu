# 第一篇 · 基础与全景

## 第 1 章 计算材料学的位置

### 1.1 材料科学的"四个支柱"

经典：
1. **加工** (Processing)
2. **结构** (Structure)
3. **性能** (Properties)
4. **性能表现** (Performance)

**关键关系**：
$$ \text{Processing} \to \text{Structure} \to \text{Properties} \to \text{Performance} $$

每个箭头都是一个研究方向。

### 1.2 计算材料学的角色

**传统**：每个箭头靠**实验测**——耗时贵慢。

**计算**：每个箭头都可以**算**：

| 关系 | 计算方法 |
|---|---|
| Processing → Structure | CALPHAD + Phase-field + KMC |
| Structure → Properties | DFT + MD + CP-FEM |
| Properties → Performance | FEM + Multi-physics |

### 1.3 ICME (Integrated Computational Materials Engineering)

NIST 2008 定义：

> "ICME 把计算模型 + 实验数据 + 材料行为整合到产品设计中"

**核心**：
- **从 atom 到 工程产品**
- **每个尺度都算**
- **信息流连续**
- **闭环优化**

### 1.4 为什么 2024 是历史拐点

3 个 game changers：

**1. MACE-MP-0 (2023)**
- One MLP, 89 elements
- DFT 精度 + 1000× 快
- 改变 MD 时代

**2. MatterGen / DiffCSP (2024)**
- Generative materials design
- 不只 screen，直接 generate
- 反向设计变可行

**3. Universal foundation models**
- 类似 LLM 在 NLP
- 一个 model 多任务
- 实验/计算闭环加速

**结果**：计算材料 paradigm 从 "tool" → "co-pilot"。

### 1.5 你的位置

读这本书的你应该问：

- 我现在**在哪一步**？（初学 / 单方法熟 / 多方法新 / 已有 ICME 经验）
- 我**最缺什么**？
- 我**5 年想到哪**？

**典型 path**：
- Year 0: 读这本书
- Year 1: 1-2 方法独立 + 第一篇 paper
- Year 3: 完整 ICME workflow
- Year 5: 独立 niche + 顶刊 + recognized

## 第 2 章 数理基础

### 2.1 必备数学

| 模块 | 用在哪 |
|---|---|
| 微积分 | 几乎所有 |
| 线性代数 | DFT + 数值 |
| 概率统计 | MC + ML + UQ |
| 偏微分方程 (PDE) | Phase-field + CP-FEM |
| 数值分析 | 所有计算 |
| 群论 | 晶体学 + 对称 |
| 傅里叶分析 | DFT + 信号 |

**关键技能**：
- 能读懂教科书公式
- 能 implement 简单数值算法
- 能用 Python 数值库

### 2.2 必备物理化学

| 模块 | 用在哪 |
|---|---|
| 量子力学 | DFT 基础 |
| 统计力学 | MD + MC + 相变 |
| 热力学 | CALPHAD + 平衡 |
| 固体物理 | 能带 + 缺陷 |
| 晶体学 | 所有原子模拟 |
| 反应动力学 | KMC + 扩散 |

**入门资源**：
- Griffiths《Quantum Mechanics》
- Kittel《Introduction to Solid State Physics》
- Atkins《Physical Chemistry》
- Reif《Statistical Physics》

### 2.3 必备编程

**核心**：**Python**

```python
import numpy as np          # 数值
import scipy as sp          # 科学计算
import matplotlib.pyplot as plt  # 画图
import pandas as pd         # 数据
```

**材料特定**：

```python
import ase                  # Atomic Simulation Environment
import pymatgen             # Materials Project
from mp_api.client import MPRester  # MP API
import phonopy              # 声子
import pycalphad            # CALPHAD
```

**ML/AI**：

```python
import torch
import torch_geometric      # GNN
from mace.calculators import mace_mp  # Universal MLP
import botorch              # Bayesian Optimization
```

### 2.4 Linux + HPC

```bash
# 必备命令
ls cd mkdir cp mv rm
grep sed awk find
ssh scp rsync
top ps kill

# Shell scripting
for sample in $(seq 1 100); do
    ...
done

# HPC (Slurm)
sbatch run.sh
squeue -u $USER
```

### 2.5 习题

1. 用 Python 求解 1D 时间无关 Schrödinger 方程（势井）
2. 用 ASE 创建 Si 晶体并画出
3. 用 Pymatgen 从 MP 取 100 个化合物
4. 用 Linux + Slurm 提交一个并行任务

## 第 3 章 5 大方法整合视角

### 3.1 方法地图

```
         尺度  ←─── 时间 ──→
         
         |
     m   |                                     ┌─── FEM ───┐
         |                                     │           │
     mm  |                          ┌── CP-FEM ┘           │
         |                         /                       │
     μm  |              ┌── Phase-field ──┐                │
         |             /                  │                │
     nm  |        ┌── MD (MLIP) ────┐     │                │
         |       /                  │     │                │
     Å   |  ┌── DFT ──┐             │     │                │
         |  └──────────┘             └──────────────────────┘
         |  fs        ps          ns/μs    ms/s            hours
         └────────────────────────────────────────────────→
         
                 ←── ML / BO / UQ 横切所有层 ──→
```

### 3.2 5 大方法 quick recap

**1. DFT** — 电子层
- Schrödinger 方程量子求解
- 输出：能量、力、电子结构

**2. MD + MLIP** — 原子层
- 解牛顿方程
- 用 MLIP（如 MACE-MP-0）做势函数
- 输出：动力学、扩散、相变

**3. CALPHAD** — 热力学层
- Gibbs 能 + 多相平衡
- 输出：相图、driving force

**4. Phase-field** — 介观层
- PDE 求微观组织演化
- 输出：晶粒、织构、析出

**5. CP-FEM** — 宏观层
- 晶体塑性 + 有限元
- 输出：应力-应变、宏观性能

### 3.3 何时用谁（决策矩阵）

| 你想知道什么 | 主用 | 辅助 |
|---|---|---|
| 这个材料能存在吗 | DFT formation E | CALPHAD |
| 多元相图 | **CALPHAD** | DFT |
| 弹性常数 | DFT | MD |
| 扩散系数 | **MD (MLIP)** | NEB |
| 微观组织 | **Phase-field** | KMC |
| 力学响应 | **CP-FEM** | MD |
| 找最优 composition | **BO + ML** | 全 chain |
| 不确定性 | **UQ propagation** | MCMC |

### 3.4 实战示例：一个简单问题用谁

**问题**：钢的奥氏体 → 马氏体相变温度

**Method**:
- DFT：固定相能量（不太适用，温度效应难）
- MD：可以模拟，但 MLIP 需要训练
- **CALPHAD**：✓ 直接给出
- Phase-field：模拟动力学
- CP-FEM：算 phase transition 力学

**Optimal**：CALPHAD + Phase-field 联用。

### 3.5 习题

1. 给定 5 个材料问题，决定用什么方法
2. 画出 5 大方法的信息流图
3. 设计一个简单 multi-scale workflow

## 第 4 章 信息流详解

### 4.1 信息怎么从一个尺度传到下一个

**关键洞察**：**每个方法的 output 是下一个的 input**。

#### DFT → CALPHAD

DFT 算每元素的 **endmember Gibbs energy**：

$$ G_i^0(T) = E_{DFT} + ZPE + \int C_p dT - TS $$

填入 CALPHAD database（.tdb 文件）。

#### DFT → MLIP

DFT 数据训练 MLIP：

```
DFT calculations
  ├── energies (eV)
  ├── forces (eV/Å)
  └── stresses (eV/Å³)
       ↓
   Training set
       ↓
   MLIP model
```

#### MD → Phase-field

MD 给：
- **Interface energy** γ
- **Mobility** M
- **Driving force** ΔG（也可以用 CALPHAD）

填入 phase-field equation。

#### CALPHAD → Phase-field

CALPHAD 给：
- **f(c, T)** 自由能函数
- **Driving force** Δμ

Direct integration via **TC-Python** / **PyCalphad**.

#### Phase-field → CP-FEM

Phase-field 给：
- **Microstructure** (grain shape + orientation)
- **Phase distribution**

转化为 FEM mesh (via DREAM.3D + Neper)。

### 4.2 误差怎么传播

```
DFT 误差 ±20 meV/atom
    ↓
MLIP 误差 ±10 meV (累加)
    ↓
MD 性质误差 ±15%
    ↓
Phase-field 误差 ±20%
    ↓
CP-FEM 力学误差 ±15 MPa
```

**所以**：每层都需要 UQ。

详见第九篇 UQ propagation。

### 4.3 数据格式 + 接口

| 格式 | 用途 |
|---|---|
| **CIF** | 晶体结构 |
| **POSCAR** | VASP 结构 |
| **extxyz** | MLIP 训练 |
| **TDB** | CALPHAD database |
| **HDF5** | 大数据 trajectory |
| **VTK** | Phase-field visualization |
| **JSON** | Workflow metadata |

### 4.4 自动化 — Atomate / FireWorks

```python
from atomate2.vasp.flows.elastic import ElasticMaker
from jobflow.managers.local import run_locally

flow = ElasticMaker().make(structure)
result = run_locally(flow)
```

一个命令 → DFT 跑完 → 后处理 → 数据库存。

### 4.5 习题

1. 给一个 CALPHAD 文件 (.tdb)，提取一个 Gibbs 能函数
2. 把 VASP OUTCAR 转 extxyz
3. 设计一个 5-step ICME workflow

## 第 5 章 软件工具栈

### 5.1 必装清单

| 类别 | 软件 | 难度 | License |
|---|---|---|---|
| **DFT** | Quantum Espresso | ★★ | **免费** |
| | VASP | ★★ | 商用 |
| | GPAW | ★ | 免费 |
| **MD** | LAMMPS | ★★ | **免费** |
| | ASE | ★ | 免费 |
| **MLIP** | MACE | ★★ | **免费** |
| | DeepMD | ★★★ | 免费 |
| **CALPHAD** | PyCalphad | ★ | **免费** |
| | Thermo-Calc | ★★ | 商用 |
| **Phase-field** | MOOSE | ★★★ | **免费** |
| | FiPy | ★ | 免费 |
| | PRISMS-PF | ★★★ | 免费 |
| **CP-FEM** | DAMASK | ★★★ | **免费** |
| | ABAQUS | ★★ | 商用 |
| **ML** | scikit-learn | ★ | **免费** |
| | PyTorch | ★★ | 免费 |
| **BO** | BoTorch | ★★ | **免费** |
| **UQ** | emcee / SALib | ★★ | **免费** |
| **可视化** | VESTA | ★ | **免费** |
| | OVITO | ★ | 免费 |
| | Paraview | ★★ | 免费 |

**全免费版本可以做完整 ICME**。

### 5.2 推荐 conda env

```yaml
# environment.yml
name: compmat
channels:
  - conda-forge
  - pytorch
  - nvidia
dependencies:
  - python=3.11
  - numpy scipy matplotlib pandas
  - pytorch pytorch-cuda=12.1
  - ase pymatgen mp-api
  - lammps
  - quantum-espresso
  - pip:
    - mace-torch
    - botorch
    - emcee
    - SALib
    - pycalphad
    - torch_geometric
```

```bash
conda env create -f environment.yml
conda activate compmat
```

### 5.3 HPC 部署

```bash
# Slurm submission
#!/bin/bash
#SBATCH --job-name=ICME
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --gpus=4
#SBATCH --time=24:00:00

module load vasp quantum-espresso lammps

# Run
mpirun -np 128 vasp_std
```

### 5.4 数据管理

```
project_root/
├── data/
│   ├── raw_dft/
│   ├── processed/
│   └── mlip_models/
├── results/
│   ├── md_traj/
│   ├── phase_field/
│   └── cpfem/
├── notebooks/
├── code/
└── papers/
```

**关键**：版本控制（Git）+ 数据备份（每周）+ 文档（每个 result 一个 README）。

---


# 任 脉 · 自下而上 · 物理建模链 / Ren-meridian — Physics-based ladder (Bottom-up)

*任脉从这里开始：从电子尺度出发，每上一层尺度 ×10², 时间 ×10⁴。共 5 步：DFT → MD/MLIP → CALPHAD → Phase-field → CP-FEM*

*你正在迈出第 1 步：电子尺度的 DFT*
