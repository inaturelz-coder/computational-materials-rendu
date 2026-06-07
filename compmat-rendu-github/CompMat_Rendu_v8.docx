# 打通计算材料学任督二脉 / CompMat Rendu

> **Bridging the Threads of Computational Materials Science**
> *把 53 章貌似零散的方法，编织成你大脑里随时可调用的网*

Author: **Li Zhou**
Email: lizhou_alfred2011@hotmail.com
Edition: v8 · 2026
License: MIT

---

## 关于本书 / About

这是《打通系列》的第三弹——继《打通物理任督二脉》和《打通工科数学任督二脉》之后，给**懂材料但还不懂计算**的研究者写的一本**贯通式**计算材料学教材。

它的目标：**1 年内**把读者从"听说过 DFT/MLIP/CALPHAD/相场"带到"能独立设计 + 执行 ICME 工作流"。

---

## 二脉框架 / Two-Meridians Framework

### 任脉 · 自下而上 · 物理建模链 (Ren-meridian)

```
电子 (0.1 nm, fs)   ── DFT              ── 第二篇 (Ch 6-9)
   ↓
原子 (1 nm, ps)     ── MD / MLIP        ── 第三篇 (Ch 10-13)
   ↓
热力学 (100 nm, eq) ── CALPHAD          ── 第四篇 (Ch 14-18)
   ↓
介观 (μm, hour)     ── Phase-field      ── 第五篇 (Ch 19-23)
   ↓
连续 (mm-m, year)   ── CP-FEM / FEM     ── 第六篇 (Ch 24-27)
```

### 督脉 · 自外而内 · 数据驱动闭环 (Du-meridian)

```
表征 (实验) → ML / GNN → BO / 主动学习 → UQ → (回到 BO)
第十篇         第七篇        第八篇         第九篇
```

### 两脉交汇 = ICME

第十一篇 (Ch 44-51)：Inconel 718 设计 + 增材制造的完整 case study，任脉物理建模 + 督脉数据闭环合流。

---

## 仓库结构 / Repository Structure

```
compmat-rendu/
├── README.md                     ← 本文件
├── LICENSE                       ← MIT
├── requirements.txt              ← Python deps
├── docs/                         ← 编译产物 + 源 markdown
│   ├── CompMat_Rendu_v8.pdf      (196 页终版 PDF)
│   ├── CompMat_Rendu_v8.docx     (Word 版)
│   └── CompMat_Book_v8.md        (Markdown 源)
├── chapters/                     ← 12 篇拆分 markdown
│   ├── 00_preface_two_meridians.md
│   ├── 01_part1_basics.md
│   ├── 02_ren1_dft.md            (任脉 1: DFT)
│   ├── 03_ren2_md_mlip.md        (任脉 2: MD + MLIP)
│   ├── 04_ren3_calphad.md        (任脉 3: CALPHAD)
│   ├── 05_ren4_phasefield.md     (任脉 4: Phase-field)
│   ├── 06_ren5_cpfem.md          (任脉 5: CP-FEM)
│   ├── 07_du2_ml.md              (督脉 2: ML)
│   ├── 08_du3_bo_mc.md           (督脉 3: BO + MCMC)
│   ├── 09_du4_uq.md              (督脉 4: UQ)
│   ├── 10_du1_characterization.md(督脉 1: 表征)
│   ├── 11_icme_confluence.md     (两脉交汇)
│   └── 12_future_path.md         (收尾)
└── modules/                      ← 一篇一模块的 Python 实现
    ├── m01_basics.py             (常数 + 单位换算 + 形成能)
    ├── m02_dft.py                (Birch-Murnaghan EOS 拟合, DOS-gap, 收敛检查)
    ├── m03_md_mlip.py            (LJ NVE MD, RDF, MLIP 接口 stub)
    ├── m04_calphad.py            (Regular solution, spinodal, RK 展开)
    ├── m05_phasefield.py         (1-D Cahn-Hilliard Eyre 半隐式格式)
    ├── m06_cpfem.py              (Schmid factor, Voigt-Reuss-Hill, Mises/Tresca)
    ├── m07_ml.py                 (从零实现 GP + RBF 核 + LOO-CV)
    ├── m08_bo.py                 (EI 采集, BO loop, Metropolis-Hastings)
    ├── m09_uq.py                 (MC 前向, bootstrap CI, Sobol 指数)
    ├── m10_characterization.py   (XRD Bragg, Williamson-Hall, pseudo-Voigt)
    ├── m11_icme.py               (5 阶段串联: DFT→CALPHAD→PF→CP-FEM→BO+UQ)
    ├── m12_software_path.py      (环境检查 + 5 年成长路径)
    └── test_all_modules.py       (一键跑全部 demo)
```

---

## 快速开始 / Quick Start

```bash
git clone <repo>
cd compmat-rendu
pip install numpy scipy matplotlib pandas scikit-learn   # 最小依赖

# 跑全部 12 个模块的 demo
cd modules
python test_all_modules.py

# 单独跑某个 demo
python m05_phasefield.py    # 看 Cahn-Hilliard 演化
python m11_icme.py          # 看 5 阶段 ICME 串联
```

每个模块都可以独立运行，输入输出说明放在 `__doc__` 里。

---

## 12 篇 / 53 章 (按二脉分类)

### 第〇部分 · 入门与全景 (Foundation)
- 第一篇：基础与全景 (Ch 1-5)

### 任脉 · 自下而上 (Ren-meridian)
- 第二篇：量子层 DFT (Ch 6-9)
- 第三篇：原子层 MD + MLIP (Ch 10-13)
- 第四篇：热力学层 CALPHAD (Ch 14-18)
- 第五篇：介观层 Phase-field (Ch 19-23)
- 第六篇：宏观层 CP-FEM (Ch 24-27)

### 督脉 · 自外而内 (Du-meridian)
- 第十篇：表征 — 数据源头 (Ch 40-43)
- 第七篇：ML for Materials (Ch 28-31)
- 第八篇：BO + MC + 主动学习 (Ch 32-35)
- 第九篇：UQ — 不确定性量化 (Ch 36-39)

### 两脉交汇 · ICME
- 第十一篇：ICME 完整闭环 (Ch 44-51)

### 收尾
- 第十二篇：软件生态 + 5 年成长路径 (Ch 52-53)

---

## 模块之间的依赖关系

```
m01 (basics)        — standalone
m02 (dft)           — standalone
m03 (md_mlip)       — standalone
m04 (calphad)       — standalone
m05 (phasefield)    — standalone
m06 (cpfem)         — standalone
m07 (ml)            — standalone (GP 实现)
m08 (bo)            — uses m07
m09 (uq)            — standalone
m10 (charact.)      — standalone
m11 (icme)          — uses m02, m04, m05, m06, m07, m08, m09 (整合)
m12 (software_path) — standalone (env check + roadmap)
```

`m11_icme.py` 是教学的高点 —— 看它就懂为什么前 10 个模块这么设计。

---

## 引用 / Citation

```bibtex
@book{zhou2026compmat_rendu,
  author = {Li Zhou},
  title  = {打通计算材料学任督二脉 / Bridging the Threads of Computational Materials Science},
  year   = {2026},
  edition= {v8},
  url    = {https://github.com/<user>/compmat-rendu}
}
```

---

*MIT License · Li Zhou · 2026*
