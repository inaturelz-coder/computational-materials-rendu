# 第十篇 · 督脉第 1 阶段：表征 — 数据源头

*督脉的起点是真实世界的实验数据。本篇覆盖 XRD/SEM/TEM/EDS/XPS/SAXS/In-situ*
*下游：数据喂给第七篇 ML 建模、给第八篇 BO 验证、给第九篇 UQ 标定*

## 第 40 章 XRD 全套

### 35.1 物理原理 — Bragg 与衍射强度

**Bragg 条件**：
$$2 d_{hkl} \sin\theta = n \lambda$$

但 Bragg 只告诉"哪里会有峰"，强度还需要 **结构因子**：

$$F_{hkl} = \sum_j f_j \exp[2\pi i (h x_j + k y_j + l z_j)]$$

衍射强度（粉末）：
$$I_{hkl} \propto |F_{hkl}|^2 \cdot L_p(\theta) \cdot P_{hkl} \cdot \text{abs}(\theta) \cdot \text{prefF}$$

其中：
- $L_p(\theta) = \frac{1 + \cos^2 2\theta}{\sin^2\theta \cos\theta}$ — Lorentz-Polarization 因子
- $P_{hkl}$ — 多重性（cubic (100) 是 6, (111) 是 8）
- abs — 吸收因子
- prefF — 择优取向因子（March-Dollase 模型）

### 35.2 数据分析 5 步法

**Step 1：相鉴定（Phase ID）**
- 找峰位 + 强度比 → 匹配 PDF 数据库（ICDD）
- Python：`pymatgen.analysis.diffraction.xrd.XRDCalculator`

```python
from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure

struct = Structure.from_file("FCC_Fe.cif")
xrd = XRDCalculator(wavelength="CuKa")
pattern = xrd.get_pattern(struct, two_theta_range=(20, 90))

import matplotlib.pyplot as plt
plt.plot(pattern.x, pattern.y, '-')
for tt, hkl, d in zip(pattern.x, pattern.hkls, pattern.d_hkls):
    plt.text(tt, max(pattern.y)*0.05, f"({hkl[0]['hkl']})", rotation=90)
```

**Step 2：峰拟合（Profile fit）**
单峰用 pseudo-Voigt：
$$\text{pV}(2\theta) = \eta L(2\theta) + (1-\eta) G(2\theta)$$

L = Lorentzian (低尾长)，G = Gaussian (中间峰)，$\eta$ 混合参数。

**Step 3：晶格常数（最小二乘）**
对每条 $(hkl)$ 用 Bragg 算 $d_{hkl}$，反推 $a, b, c, \alpha, \beta, \gamma$。

立方系：
$$\frac{1}{d_{hkl}^2} = \frac{h^2 + k^2 + l^2}{a^2}$$

**Step 4：晶粒大小（Scherrer）**
$$D = \frac{K \lambda}{\beta \cos\theta}$$
$K \approx 0.94$（球状 FWHM 形状因子），$\beta$ 为 FWHM（弧度）。

> 注意：Scherrer 不考虑**应变** broadening！只准 < 200 nm。

**Step 5：晶粒大小 + 应变（Williamson-Hall）**
$$\beta \cos\theta = \frac{K\lambda}{D} + 4\epsilon \sin\theta$$

画 $\beta\cos\theta$ vs $\sin\theta$：截距给 D，斜率给 $\epsilon$。

```python
import numpy as np
# 数据 (例)
peaks = [(31.7, 0.15), (45.5, 0.18), (66.4, 0.22)]  # (2θ, FWHM in deg)
lam = 1.5406  # CuKa

theta_rad = np.array([p[0]/2 * np.pi/180 for p in peaks])
beta_rad = np.array([p[1] * np.pi/180 for p in peaks])

x = np.sin(theta_rad)
y = beta_rad * np.cos(theta_rad)
slope, intercept = np.polyfit(x, y, 1)

D_nm = 0.94 * lam / intercept  # in Å × 10
strain = slope / 4
print(f"晶粒 D = {D_nm:.1f} Å, 应变 ε = {strain*100:.2f}%")
```

### 35.3 Rietveld 精修

整谱拟合，可同时算：
- 晶格常数（高精度，1 ppm）
- 原子位置 + 占位率
- 热振动参数（B-factor）
- 相含量（多相）
- 织构

**Rwp（加权残差）**：
$$R_{wp} = \sqrt{\frac{\sum_i w_i (y_i^{obs} - y_i^{calc})^2}{\sum_i w_i (y_i^{obs})^2}}$$

合格标准：$R_{wp} < 10\%$，χ² < 2-3。

**软件**：GSAS-II（最常用，免费）、FullProf、TOPAS（商业，速度快）。

### 35.4 ML 辅助 XRD 相分析

传统人工 phase ID 慢，新趋势用 CNN 自动识别。

```python
# 简化版：用 1D-CNN 识别二相混合
import torch.nn as nn
class XRDCNN(nn.Module):
    def __init__(self, n_phases=230):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(1, 32, 5), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 5), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(64, 128, 3), nn.ReLU(), nn.AdaptiveAvgPool1d(1)
        )
        self.fc = nn.Linear(128, n_phases)  # 多标签输出
    def forward(self, x):
        x = self.conv(x).squeeze(-1)
        return torch.sigmoid(self.fc(x))  # 每相独立概率

# 训练数据：合成 XRD（用 pymatgen 给 ICSD ~10k 化合物算），加噪声
# 验证：Sun-Group 2019 Nature, F1 > 0.85 in mixture phase
```

### 35.5 习题

**习题 35.1**：用 Scherrer 测得晶粒 D = 80 nm，但 TEM 测得是 40 nm。哪里出错？

**答**：Scherrer 假设零应变。若样品有微应变，FWHM 包含应变 broadening → 算出的 D 偏大。用 Williamson-Hall 分离两效应，D 会减小到接近 TEM 值。

## 第 41 章 电镜全套

### 36.1 SEM 信号来源与对比度

电子束（5-30 kV）打到样品，发出多种信号：

| 信号 | 信息深度 | 提供信息 |
|------|----------|----------|
| 二次电子 (SE) | < 10 nm | 表面形貌 |
| 背散射电子 (BSE) | 50-200 nm | Z 衬度（成分） |
| 特征 X 射线 | 1-5 μm | 元素组成 (EDS) |
| 阴极荧光 (CL) | μm | 半导体/绝缘体能带 |
| 透射电子 (STEM-in-SEM) | 全 | 晶体结构 |

**对比度公式**（BSE）：
$$\eta \approx Z^{0.4}, \quad \text{所以 } \Delta \eta \approx 0.4 \frac{\Delta Z}{Z} \eta$$

可以区分 Z 差 1 的元素，但不能区分同 Z 不同价态。

### 36.2 EDS 定量

**ZAF 校正**：
$$C_i = k_i \cdot Z_i \cdot A_i \cdot F_i$$

- Z = 原子序数校正
- A = 吸收校正
- F = 荧光校正

实测信号 $k_i$ 用标准样品比对。误差通常 ±2-5 wt%。

**EDS 局限**：
- 轻元素 (Z < 6) 难
- 弱浓度 (<1%) 误差大
- 表面氧化层会污染信号

### 36.3 EBSD 完整工作流

**原理**：电子在样品表面 70° 倾角散射，菊池带反映晶向。

**Step 1：花纹识别（Hough 变换）**
菊池带在 Hough 空间是亮点 → 提取带位置 → 反求晶面法向。

**Step 2：取向匹配**
对 N 个候选相，用预存的菊池模板匹配 → 找最佳取向 (φ1, Φ, φ2) Euler 角。

**Step 3：后处理（noise reduction + grain reconstruction）**
- 用最近邻投票去除孤立点
- Grain boundary: 临近像素取向差 > 15° = 大角晶界（HAGB）

**Step 4：分析**
- 织构（pole figure, ODF）
- 晶粒大小（intercept method）
- KAM (Kernel Average Misorientation) → 局部应变图
- Schmid factor → 滑移启动取向

```python
# MTEX 风格的 Python 替代 (pyEBSD)
import numpy as np
from orix import quaternion, vector

# 读取 EBSD 数据 (HKL .ctf 文件)
eulers = np.loadtxt("data.ctf", skiprows=6, usecols=(5,6,7))  # φ1,Φ,φ2

# 转 quaternion
q = quaternion.Orientation.from_euler(np.radians(eulers))

# 算 KAM (3x3 邻居)
# ... (省略空间索引细节)

# Pole figure
plt.figure()
q.to_pole_figure(hkl="111").plot()
```

### 36.4 TEM 高分辨

**HRTEM**：相位对比，原子柱亮暗

**STEM-HAADF**：高角度环形暗场，亮度 ∝ Z^2（强 Z 衬度）→ 直接看原子位置

**EELS（电子能量损失谱）**：
- 低损耗 (0-50 eV)：等离子体，介电常数
- 核心边缘 (50-3000 eV)：元素 + 价态
- 比 EDS 灵敏更高（轻元素 + 价态）

**4D-STEM**：每个扫描点存全部衍射图，事后可重构应变图、相图。

### 36.5 ML 辅助电镜分析

**用途 1：自动相鉴定（HRTEM 图 → 晶体相）**
- 数据：合成 HRTEM 图（用 MULTEM 模拟）+ 实验
- 模型：CNN 分类 / GNN

**用途 2：缺陷自动检测（位错、孪晶、孔洞）**
- 模型：YOLO / Mask R-CNN

**用途 3：原子级 STEM 图分析**
- 任务：找原子柱中心 → 测晶格畸变
- 模型：U-Net 语义分割 + Gaussian fit

```python
# 简化的 U-Net 找原子柱
import segmentation_models_pytorch as smp
model = smp.Unet(encoder_name="resnet34", in_channels=1, classes=1)
# 训练: 输入 STEM 灰度图, 输出原子柱二值掩码
# 推理后用 scipy.ndimage.center_of_mass 找每柱中心
```

## 第 42 章 XPS 与 BET 与小角散射

### 37.1 XPS 表面化学

$$E_{KE} = h\nu - E_{BE} - \phi$$

测 KE → 算 BE → 元素 + 价态。穿透深度 1-10 nm（极表面）。

**关键应用**：
- 元素鉴定（峰位）
- 价态分析（化学位移：Fe⁰ vs Fe³⁺ 差 5-7 eV）
- 表面成分（定量，±10% 内）
- 深度剖面（用 Ar⁺ 溅射 + 重复 XPS）

**拟合软件**：CasaXPS、XPSPEAK

### 37.2 BET 比表面

**等温吸附**：
$$\frac{p/p_0}{V(1-p/p_0)} = \frac{C-1}{V_m C} \cdot \frac{p}{p_0} + \frac{1}{V_m C}$$

画线性图 → 截距 + 斜率 → $V_m$ → 单层覆盖面积 $S$。

适用 $0.05 < p/p_0 < 0.30$。微孔材料用 t-plot 或 DFT 法。

### 37.3 SAXS 小角散射

测 1-100 nm 尺度。

**Guinier 区**（低 q）：
$$I(q) \approx I(0) \exp(-q^2 R_g^2 / 3)$$
给 $R_g$（回转半径）。

**Porod 区**（高 q）：
$$I(q) \propto S \cdot q^{-4}$$
给比表面积 $S$。

## 第 43 章 原位 / 4D 表征

### 38.1 原位 XRD（in-situ）

加温 / 加力 / 加电压 → 实时跟踪相变 / 应变。

**典型实验**：
- 钛合金 α→β 转变温度（每 5°C 拍一次）
- 锂电充放电时阴极相变
- 焊接热影响区原位 monitoring

### 38.2 同步辐射

亮度比实验室源高 10^9，光斑可聚焦到 100 nm。

**主要技术**：
- HEXRD（高能 XRD）：穿透 5 mm 钢，原位
- XANES：边缘前结构 → 价态、配位
- EXAFS：边缘后振荡 → 局部原子环境（键长 ±0.02 Å）

### 38.3 数据反演 — 从光谱到结构

XANES 反演价态：
1. 测样品 XANES
2. 与标准化合物（Fe⁰, FeO, Fe2O3）线性组合
3. 比例 = 各价态含量

EXAFS 反演键长：
$$\chi(k) = \sum_j \frac{N_j S_0^2}{k R_j^2} f_j(k) \exp(-2 R_j / \lambda(k)) \exp(-2 \sigma_j^2 k^2) \sin(2 k R_j + \phi_j(k))$$

软件：Demeter (ATHENA + ARTEMIS)，IFEFFIT。

---


