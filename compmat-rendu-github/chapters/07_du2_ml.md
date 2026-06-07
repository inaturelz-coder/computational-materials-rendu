# 第七篇 · 督脉第 2 阶段：ML for Materials

## 第 28 章 材料 ML 全景

### 23.1 为什么 ML 改变了材料科学

经典材料发现的瓶颈：

| 范式 | 周期 | 成本 | 覆盖空间 |
|------|------|------|----------|
| 试错 (1900-1980) | 10-20 年 | 10^7 美金 | 10^3 候选 |
| 高通量实验 (1990-2010) | 3-5 年 | 10^6 美金 | 10^5 候选 |
| 高通量 DFT (2010-2020) | 1-2 年 | 10^5 美金 | 10^6 候选 |
| ML 加速 (2020-) | 周-月 | 10^4 美金 | 10^9 候选 |

**关键洞察**：化学组分空间 ≈ 10^60（80 种元素任意比例），DFT 算不完，ML 是唯一可能扫完的方法。

### 23.2 材料 ML 三大范式

**范式 A：性质预测（监督学习）**
- 输入：结构/组分 → 输出：性质（带隙、形成能、弹性模量）
- 数据：Materials Project、AFLOW、OQMD、JARVIS
- 模型：Random Forest、GBM、GNN、Transformer

**范式 B：生成模型（无监督）**
- 给定目标性质 → 生成新结构/组分
- 模型：VAE、GAN、Diffusion、Flow

**范式 C：主动学习（闭环）**
- 模型预测 → 实验/DFT 验证 → 反馈训练 → 选下一个
- 模型：BO + GPR + acquisition function

### 23.3 材料表征（Featurization）

ML 第一难题：怎么把"结构/组分"变成数值向量？

**层次 1：组分特征（Composition-based）**
- 元素属性求和/平均：电负性、半径、价电子数
- 工具：matminer 的 `ElementProperty`
- 优点：快，无需结构
- 缺点：同组分异结构无法区分

```python
from matminer.featurizers.composition import ElementProperty
from pymatgen.core import Composition

ep = ElementProperty.from_preset("magpie")
features = ep.featurize(Composition("Fe2O3"))
# 132 维向量：均值、方差、最大、最小、范围 × 22 种属性
```

**层次 2：结构特征（Structure-based）**
- Coulomb Matrix：M_ij = Z_i Z_j / |r_i - r_j|
- SOAP：局部原子环境
- Voronoi tessellation：配位多面体
- 工具：matminer + dscribe

**层次 3：图特征（Graph-based）**
- 节点 = 原子，边 = 键
- 节点特征：元素类型、配位数
- 边特征：键长、键角
- 模型：CGCNN、MEGNet、SchNet

### 23.4 经典 ML 模型对比

| 模型 | 数据需求 | 训练时间 | 解释性 | 性能 | 典型用途 |
|------|----------|----------|--------|------|----------|
| Linear Regression | 100+ | 秒 | 高 | 低 | baseline |
| Random Forest | 1k+ | 分钟 | 中 | 中 | tabular 性质 |
| Gradient Boosting (XGBoost/LGBM) | 1k+ | 分钟 | 中 | 高 | tabular 性质 |
| 支持向量机 (SVM/SVR) | 1k+ | 分钟 | 低 | 中 | 小样本 |
| 高斯过程 (GP) | <500 | 慢 | 中 | 中 | 主动学习 |
| 神经网络 (MLP) | 10k+ | 时 | 低 | 高 | 复杂关系 |
| 图神经网络 (GNN) | 10k+ | 时 | 低 | 最高 | 结构性质 |

### 23.5 端到端 pipeline（matminer + scikit-learn）

完整带隙预测案例：

```python
import pandas as pd
from matminer.datasets import load_dataset
from matminer.featurizers.composition import ElementProperty, Stoichiometry, ValenceOrbital
from matminer.featurizers.conversions import StrToComposition
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# 1. 加载数据 (Materials Project 子集，约 1万条)
df = load_dataset("matbench_expt_gap")  # ~ 4600 个 expt. band gap
print(df.head())  # composition (str), gap (eV)

# 2. 特征化
df = StrToComposition().featurize_dataframe(df, "composition")
featurizers = [ElementProperty.from_preset("magpie"),
               Stoichiometry(), ValenceOrbital(props=["frac"])]
for f in featurizers:
    df = f.featurize_dataframe(df, "composition")

# 3. 选特征列
feat_cols = [c for c in df.columns if c not in ["composition", "gap expt"]]
X = df[feat_cols].fillna(0).values
y = df["gap expt"].values

# 4. 训练
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=42)
rf.fit(X_tr, y_tr)

# 5. 评估
pred = rf.predict(X_te)
print(f"MAE: {mean_absolute_error(y_te, pred):.3f} eV")
print(f"R²:  {r2_score(y_te, pred):.3f}")
# 典型结果: MAE ~0.45 eV, R² ~0.75
```

## 第 29 章 图神经网络深度

### 24.1 图卷积的本质

传统 CNN 处理网格（图片），但晶体/分子是图。图卷积要解决两件事：
1. 节点信息聚合（邻居 → 自己）
2. 不变性（旋转、平移、置换）

**消息传递机制（Message Passing）**：

$$h_i^{(l+1)} = \text{Update}\left(h_i^{(l)}, \text{Aggregate}\left(\{m_{ij}^{(l)} : j \in N(i)\}\right)\right)$$

其中 $m_{ij}^{(l)} = \text{Message}(h_i^{(l)}, h_j^{(l)}, e_{ij})$。

不同 GNN 的区别就在 Message / Aggregate / Update 三个函数的设计。

### 24.2 CGCNN（Crystal Graph CNN, 2018）

第一个为晶体设计的 GNN（Xie & Grossman）。

**图构造**：
- 节点 = 原子（92 维 one-hot）
- 边 = Voronoi 邻居（含距离 RBF expansion）

**卷积**：

$$v_i^{(t+1)} = v_i^{(t)} + \sum_{j, k} \sigma(z_{(i,j)_k}^{(t)} W_f + b_f) \odot g(z_{(i,j)_k}^{(t)} W_s + b_s)$$

其中 $z = v_i \oplus v_j \oplus u_{(i,j)_k}$，$\sigma$ 为 sigmoid 门控，$g$ 为 softplus。

**池化**：所有原子 embedding 平均 → 全连接 → 性质

**性能**：在 Materials Project ~50k 数据上，形成能 MAE ~0.04 eV/atom。

### 24.3 SchNet（2017-2018）

针对分子设计，但被广泛用于晶体（含 Materials Project 数据）。

**核心创新**：连续滤波器卷积

$$x_i^{(l+1)} = \sum_j x_j^{(l)} \odot W^{(l)}(\|r_i - r_j\|)$$

其中 $W^{(l)}$ 是个把距离映射到滤波器的 MLP。

**优势**：
- 严格距离不变性（不用键长 cutoff）
- 平滑梯度（可微）
- 支持力场预测（势能对位置求导）

### 24.4 MEGNet（Materials Project, 2019）

加入了**全局态**（global state，$u$），可以编码温度、压力等。

更新规则：

$$\begin{aligned}
e_k' &= \phi_e(v_{s_k} \oplus v_{r_k} \oplus e_k \oplus u) \\
v_i' &= \phi_v(v_i \oplus \bar{e}_i' \oplus u) \\
u' &= \phi_u(\bar{v}' \oplus \bar{e}' \oplus u)
\end{aligned}$$

可用于温度依赖性质（电导率 vs T）。

### 24.5 等变神经网络（Equivariant GNN）

CGCNN/SchNet/MEGNet 只能学习**标量**性质（能量、带隙）。要预测**矢量/张量**（力、应力、磁矩），需要等变性。

**等变性定义**：
$$f(R \cdot x) = R \cdot f(x)$$
即输入旋转 R，输出按 R 同步旋转。

**典型架构**：
- NequIP (2021)
- MACE (2022)
- Allegro (2023)
- SevenNet (2024)

**关键技术**：球谐函数表示矢量，张量积保持等变性。

### 24.6 GNN 代码：MEGNet 训练带隙

```python
from megnet.models import MEGNetModel
from megnet.data.crystal import CrystalGraph
from pymatgen.ext.matproj import MPRester

# 1. 拿数据
with MPRester("YOUR_API_KEY") as m:
    docs = m.summary.search(
        fields=["material_id", "structure", "band_gap"],
        num_chunks=10, chunk_size=500
    )
structures = [d.structure for d in docs]
gaps = [d.band_gap for d in docs]

# 2. 构图
cg = CrystalGraph(cutoff=4.0)
model = MEGNetModel(
    nfeat_edge=100, nfeat_global=2, nfeat_node=16,
    n_blocks=3, lr=1e-3, n1=64, n2=32, n3=16,
    graph_converter=cg
)

# 3. 训练
model.train(
    structures, gaps,
    epochs=100, batch_size=64,
    validation_structures=val_str, validation_targets=val_y
)

# 4. 预测
pred = model.predict_structure(new_structure)
print(f"Predicted band gap: {pred:.3f} eV")
```

## 第 30 章 大模型时代材料 ML

### 25.1 通用预训练模型

**MatBERT** (2022)：BERT 风格 transformer，对 2 百万材料文摘预训练。可做 NER、关系抽取。

**M3GNet** (2022)：第一代通用势 + 性质多任务，支持 89 种元素。

**MACE-MP-0** (2023)：见 12 章。

**CHGNet** (2023)：加入磁矩信息的 universal MLP，Materials Project 数据训练。

**MatterSim** (2024)：覆盖 0-5000 K, 0-1000 GPa 的 universal potential。

**ALIGNN** (Atomistic Line Graph NN, 2021)：节点 + 边 + 三体角度，性能优于 CGCNN。

### 25.2 Foundation Model for Materials

类似 LLM，趋势是「预训练 + 微调」：

1. **预训练阶段**：在 Materials Project (~150k) + AFLOW (~3M) + Alexandria (~80M) 上自监督学习
2. **微调阶段**：在用户的 500-1000 条特定数据上 fine-tune

**zero-shot vs few-shot vs fine-tune**：
- Zero-shot：直接用预训练模型预测（如 MACE-MP-0 算势能）
- Few-shot：给 10-100 个样例 + 预训练特征 → 简单回归器
- Fine-tune：500-1000 条数据，调整最后几层

### 25.3 LLM 在材料科学的应用

**用途 1：文献挖掘**
```python
from transformers import pipeline
ner = pipeline("ner", model="lbnlp/MatBERT-base-uncased")
text = "Ti6Al4V exhibits a yield strength of 880 MPa at 25 °C."
print(ner(text))
# 提取: 材料=Ti6Al4V, 性质=yield strength, 值=880 MPa
```

**用途 2：合成路径建议**
- 给 LLM 目标化合物 → 输出可能的前驱体 + 温度路径
- 已有 LLM-Reaxys、ChemCrow 等工具

**用途 3：自动 DFT 输入文件生成**
- 用户描述："我想算 Cu 表面的 H 吸附"
- LLM 生成完整 QE / VASP 输入

**用途 4：数据清洗**
- 把杂乱无章的 Excel/PDF 摘要变成结构化 DataFrame

### 25.4 多模态材料 AI

未来方向：组分 + 结构 + 显微图 + XRD + 文献摘要 都进同一个模型。

**示例架构**：
- 结构 encoder：GNN
- 图像 encoder：ViT
- 文本 encoder：BERT
- 融合：cross-attention transformer

**典型工作**：MIT 的 MultiMat (2024), DeepMind 的 GNoME (2023, 220 万新材料)。

## 第 31 章 ML 工程实战

### 26.1 数据策略

**数据集合并三规则**：

| 来源 | 优点 | 注意 |
|------|------|------|
| Materials Project | 大 (150k) | 多 PBE，可能不准 |
| AFLOW | 全 (3M+) | 子集质量参差 |
| OQMD | 大 (1M+) | 自动 PBE |
| ICSD/COD | 实验结构 | 无性质 |
| 自己的实验数据 | 准 | 少 |

**策略**：用大数据 pretrain，用实验 fine-tune。

### 26.2 train/val/test split 的陷阱

**陷阱 1：随机分割**
化学组分相近的样本可能跨集分布 → 测试集"假漂亮"。

**陷阱 2：组分泄漏**
训练集有 Fe2O3，测试集有 Fe3O4 → 性能高估。

**正确做法**：按元素或化学式分组分割（GroupKFold）。

```python
from sklearn.model_selection import GroupKFold
groups = df["composition"].apply(lambda c: ",".join(sorted(c.elements)))
gkf = GroupKFold(n_splits=5)
for tr, te in gkf.split(X, y, groups=groups):
    # 训练集和测试集化学组分不重叠
    ...
```

### 26.3 不确定性量化（材料 ML 特化）

材料 ML 用三种 UQ：

**A. Ensemble**（最常用）
- 训练 5-10 个不同种子的模型
- 预测均值 = best，方差 = uncertainty

**B. Conformal prediction**
- 黑盒，给任意模型加 90% 覆盖区间
- 见第八篇 UQ 章节

**C. Gaussian Process**
- 自带 uncertainty，适合主动学习
- 缺点：N > 1000 慢

### 26.4 端到端项目模板

```
project/
├── data/
│   ├── raw/          # 原始下载
│   ├── processed/    # 特征化后
│   └── splits/       # train/val/test 索引
├── features/
│   └── featurizer.py # matminer pipeline
├── models/
│   ├── baselines.py  # RF / GBM
│   ├── gnn.py        # CGCNN / MEGNet
│   └── ensemble.py   # 多模型平均
├── train.py
├── evaluate.py
├── predict.py
└── notebooks/
    └── eda.ipynb
```

### 26.5 习题与答案

**习题 23.1**：在带宽预测里，为什么直接用元素电负性作为唯一特征不够？

**答**：电负性只反映元素属性的均值，但材料带隙依赖结构（同样 Si-O 可形成石英、α-石英、SiO2 玻璃 → 带隙差几个 eV）。需要至少加上结构特征（配位数、键角分布）。

**习题 24.1**：CGCNN 用 Voronoi 邻居而不是固定 cutoff，原因？

**答**：cutoff 在不同密度晶体里会漏边或加错边（如低密度气固相 vs 致密金属）。Voronoi 自适应，且每个原子的"邻居数"由化学环境决定，更鲁棒。

**习题 25.1**：MACE-MP-0 在 zero-shot 模式预测高熵合金混合焓，预期误差是？怎么改善？

**答**：典型 MAE 50-100 meV/atom（比 PBE-DFT 差），主要因为训练集 Materials Project 高熵合金样本少。改善方法：a) 自己跑 50-100 个高熵合金 DFT，fine-tune；b) 用 active learning 选最有不确定性的样本补数据。

---


