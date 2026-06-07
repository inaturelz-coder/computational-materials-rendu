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
Ch 40-43       Ch 28-31      Ch 32-35       Ch 36-39
```

### 两脉交汇 = ICME

第十一篇 (Ch 44-51)：Inconel 718 设计 + 增材制造的完整 case study，任脉物理建模 + 督脉数据闭环合流的典型实战。

---

## 仓库结构 / Repository Structure

```
compmat-rendu/
├── README.md                    ← 本文件
├── LICENSE                      ← MIT
├── docs/
│   ├── CompMat_Rendu_v8.pdf     ← 终版 PDF (196 页)
│   ├── CompMat_Rendu_v8.docx    ← Word 版
│   └── CompMat_Book_v8.md       ← Markdown 源
└── chapters/                    ← 12 篇 / 53 章拆分
    ├── 00_preface_two_meridians.md
    ├── 01_part1_basics.md
    ├── 02_ren1_dft.md
    ├── 03_ren2_md_mlip.md
    ├── 04_ren3_calphad.md
    ├── 05_ren4_phasefield.md
    ├── 06_ren5_cpfem.md
    ├── 07_du2_ml.md
    ├── 08_du3_bo_mc.md
    ├── 09_du4_uq.md
    ├── 10_du1_characterization.md
    ├── 11_icme_confluence.md
    └── 12_future_path.md
```

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
