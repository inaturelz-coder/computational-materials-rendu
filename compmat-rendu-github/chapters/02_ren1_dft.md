# 第二篇 · 任脉第 1 步：量子层 — DFT

## 第 6 章 DFT 理论基础

### 6.1 多体 Schrödinger 方程从头

考虑 N 电子 + M 核的系统：

$$ \hat{H} = -\sum_i \frac{\hbar^2}{2m_e}\nabla_i^2 - \sum_I \frac{\hbar^2}{2M_I}\nabla_I^2 + \sum_{i<j}\frac{e^2}{|r_i-r_j|} - \sum_{i,I}\frac{Z_I e^2}{|r_i-R_I|} + \sum_{I<J}\frac{Z_I Z_J e^2}{|R_I-R_J|} $$

**Born-Oppenheimer 近似**：核质量 >> 电子质量，分离电子 + 核运动：

$$ \Psi(\{r_i\}, \{R_I\}) \approx \Psi_e(\{r_i\}; \{R_I\}) \cdot \chi(\{R_I\}) $$

固定核位置 → 电子 Hamiltonian：

$$ \hat{H}_e = T_e + V_{ee} + V_{eN}(\{R_I\}) $$

**这是 DFT 的起点**——所有 DFT codes 都在解电子 Hamiltonian 给定固定核.

### 6.2 Hohenberg-Kohn 定理详细证明

**HK 定理 1**: 对于一组非简并电子，外势 $V_{ext}(r)$ 由基态密度 $\rho(r)$ 唯一决定（up to constant）.

**证明**（反证法）:
假设两个不同 $V_{ext}^{(1)} \neq V_{ext}^{(2)}$ 给同样基态 $\rho_0$.

那么有两个不同 Hamiltonian $H^{(1)}, H^{(2)}$ 和不同基态 $\Psi^{(1)}, \Psi^{(2)}$.

Variational principle:
$$ E^{(1)} = \langle\Psi^{(1)}|H^{(1)}|\Psi^{(1)}\rangle < \langle\Psi^{(2)}|H^{(1)}|\Psi^{(2)}\rangle = E^{(2)} + \int(V_{ext}^{(1)} - V_{ext}^{(2)})\rho_0 dr $$

同理:
$$ E^{(2)} < E^{(1)} + \int(V_{ext}^{(2)} - V_{ext}^{(1)})\rho_0 dr $$

两式相加得 $E^{(1)} + E^{(2)} < E^{(1)} + E^{(2)}$，矛盾！QED.

**HK 定理 2**: 存在一个全域泛函 $F[\rho]$ 使得总能量

$$ E[\rho] = F[\rho] + \int V_{ext}(r)\rho(r) dr $$

且基态能量是 $E[\rho]$ 的最小值，在 $\rho = \rho_0$ 时取到.

### 6.3 Kohn-Sham 方程详细推导

**问题**: $F[\rho]$ 包含 kinetic energy + electron-electron interaction，未知精确形式.

**Kohn-Sham 想法 (1965)**: 引入辅助非相互作用系统 + density 与真实相同.

设辅助系统的轨道为 $\psi_i$，密度:
$$ \rho(r) = \sum_{i=1}^N |\psi_i(r)|^2 $$

辅助系统 Hamiltonian:
$$ \hat{H}_{KS} = -\frac{\hbar^2}{2m_e}\nabla^2 + V_{KS}(r) $$

其中 $V_{KS} = V_{ext} + V_H + V_{xc}$.

- $V_H(r) = e^2 \int \frac{\rho(r')}{|r-r'|} dr'$ (Hartree)
- $V_{xc}(r) = \frac{\delta E_{xc}[\rho]}{\delta \rho(r)}$ (exchange-correlation)

**总能分解**:
$$ E[\rho] = T_s[\rho] + E_H[\rho] + E_{xc}[\rho] + \int V_{ext}\rho dr $$

- $T_s$: 非相互作用动能 (从 KS 轨道直接算)
- $E_H$: Hartree
- $E_{xc}$: 所有未知物理装在这

**所有难题归到 $E_{xc}$** 这一项.

### 6.4 SCF 算法详细

**Self-Consistent Field 迭代**:

```python
def scf_loop(rho_init, V_ext, max_iter=100, tol=1e-6):
    rho = rho_init
    
    for iteration in range(max_iter):
        # Build effective potential
        V_H = compute_hartree(rho)
        V_xc = compute_xc_potential(rho)
        V_eff = V_ext + V_H + V_xc
        
        # Solve KS equations
        epsilon_i, psi_i = solve_eigenvalue(V_eff)
        
        # New density
        rho_new = sum(|psi_i|^2 for i in occupied)
        
        # Mixing (Pulay-style)
        rho_mixed = mix(rho, rho_new, alpha=0.3)
        
        # Check convergence
        if norm(rho_mixed - rho) < tol:
            return rho_mixed, epsilon_i, psi_i
        
        rho = rho_mixed
    
    raise ConvergenceError
```

**Mixing schemes**:
- Linear: $\rho_{n+1} = \alpha \rho_n^{new} + (1-\alpha) \rho_n$
- Pulay (DIIS): 用历史信息加速
- Broyden: quasi-Newton

### 6.5 Exchange-correlation 泛函的演化

**Jacob's ladder of DFT** (Perdew):

```
天堂 (chemical accuracy)
  ↑
  | 5. Hyper-GGA + 100% exchange (HF/RPA)
  | 4. Hybrid (HSE, B3LYP, ...)
  | 3. meta-GGA (TPSS, SCAN, r²SCAN)
  | 2. GGA (PBE, PBEsol, ...)
  | 1. LDA (Hartree, no exchange/correlation)
  |
地狱 (no approximation)
```

每升一级，复杂度 + 精度都加.

**SCAN (Strongly Constrained and Appropriately Normed)**:

$$ E_{xc}^{SCAN} = E_{xc}^{TPSS} + ... $$

满足所有已知精确条件，2015 paper, 现代默认.

**HSE06** (Heyd-Scuseria-Ernzerhof):

$$ E_x^{HSE} = a E_x^{HF,SR}(\omega) + (1-a) E_x^{PBE,SR}(\omega) + E_x^{PBE,LR}(\omega) $$

with $a = 0.25, \omega = 0.2 \text{ Å}^{-1}$.

**Range-separated** 把 Coulomb interaction 分 short/long range，short range 用部分 HF.

### 6.6 平面波 + 赝势详细

**Bloch theorem**: 周期系统中

$$ \psi_{nk}(r) = e^{ik \cdot r} u_{nk}(r) $$

with $u_{nk}$ periodic.

**展开**:
$$ \psi_{nk}(r) = \sum_G c_{nk}(G) e^{i(k+G) \cdot r} / \sqrt{V} $$

with G = reciprocal lattice vectors.

**截断条件**:
$$ \frac{\hbar^2}{2m_e} |k+G|^2 \leq E_{cut} $$

**PAW (Projector-Augmented Wave)**:

把真实波函数 $\Psi$ 与平滑波函数 $\tilde\Psi$ 关联:

$$ \Psi = \tilde\Psi + \sum_i (|\phi_i\rangle - |\tilde\phi_i\rangle) \langle\tilde p_i | \tilde\Psi\rangle $$

- $\phi_i$: 真实 atomic orbitals
- $\tilde\phi_i$: smooth pseudo-orbitals
- $\tilde p_i$: projectors

**优点**: 高精度 (all-electron) + 平滑 (fewer plane waves) + 计算快.

### 6.7 k 点采样 + Brillouin Zone 积分

**Monkhorst-Pack grid**:

$$ k_{n_1 n_2 n_3} = \sum_i \frac{2n_i - N_i - 1}{2 N_i} b_i $$

with $N_i$ divisions in each direction.

**Smearing** for metals:
- Gaussian: $f(\epsilon) = \frac{1}{2}\text{erfc}\left(\frac{\epsilon}{\sigma}\right)$
- Methfessel-Paxton: 高阶 polynomial smearing (better entropy)
- Fermi-Dirac: physical T smearing

**Σ vs Σ_real**: smearing 给的 entropy 不是物理 T 的 entropy.

### 6.8 习题（含答案）

**6.1** 推导 Hohenberg-Kohn 第一定理.
**答案**: 见 §6.2.

**6.2** 写出 Kohn-Sham 方程并解释每一项.
**答案**: $\left[-\frac{\hbar^2}{2m}\nabla^2 + V_{KS}\right]\psi_i = \epsilon_i \psi_i$, with $V_{KS}=V_{ext}+V_H+V_{xc}$.

**6.3** 为什么 LDA 高估键能？
**答案**: LDA 假设 uniform electron gas，对快速变化密度过度 binding.

**6.4** Hybrid functional 慢 10× 原因.
**答案**: 精确交换 $\int\int\frac{\psi_i^*(r_1)\psi_j^*(r_2)\psi_j(r_1)\psi_i(r_2)}{|r_1-r_2|}dr_1dr_2$ scaling N⁴, vs LDA/GGA N³.

**6.5** PAW vs USPP 区别.
**答案**: PAW = all-electron via projection; USPP = pseudo with augmentation. PAW 通常更准.

## 第 7 章 DFT 实战工作流

### 7.1 软件选择详细

**VASP**:
- ✓ 最 widely used in research
- ✓ 强大但商用
- ✓ 文档好
- ✗ License €5000+/year academic

**Quantum Espresso (QE)**:
- ✓ 完全免费 GPL
- ✓ Modular (pw, ph, epw, etc.)
- ✓ HPC friendly
- ✓ 文档良好
- ✗ 略 less polished

**GPAW**:
- ✓ Python 接口最自然
- ✓ ASE 集成完美
- ✓ 免费
- ✗ 速度比 VASP/QE 略慢

**CP2K**:
- ✓ 大体系 + AIMD
- ✓ 免费
- ✓ Mixed Gaussian + plane waves
- ✗ 学习曲线陡

**ABINIT**:
- ✓ 物理深度强
- ✓ DFPT + many-body
- ✓ 免费

### 7.2 完整 Si 计算 — 6 步骤

**Step 1**: 安装 + 测试

```bash
conda install -c conda-forge qe
echo "TEST" | pw.x -test
```

**Step 2**: 准备赝势

下载 from psl (Pseudopotential Library):
```bash
wget https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

**Step 3**: SCF input

`si_scf.in`:
```
&CONTROL
    calculation = 'scf'
    prefix = 'si'
    outdir = './tmp'
    pseudo_dir = './pseudo'
    tprnfor = .true.
    tstress = .true.
    verbosity = 'high'
/
&SYSTEM
    ibrav = 2
    celldm(1) = 10.26
    nat = 2
    ntyp = 1
    ecutwfc = 50.0
    ecutrho = 400.0
    occupations = 'fixed'
/
&ELECTRONS
    conv_thr = 1.0d-10
    mixing_beta = 0.7
    diagonalization = 'david'
/
ATOMIC_SPECIES
    Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
    Si 0.00 0.00 0.00
    Si 0.25 0.25 0.25
K_POINTS automatic
    8 8 8 0 0 0
```

**Step 4**: Run

```bash
mpirun -np 8 pw.x -in si_scf.in > si_scf.out
```

Check convergence:
```bash
grep '!' si_scf.out         # Total energy
grep 'convergence' si_scf.out  # SCF iterations
```

**Step 5**: 弛豫

`si_relax.in`:
```
&CONTROL
    calculation = 'vc-relax'  ! relax cell + atoms
    ...
&IONS
    ion_dynamics = 'bfgs'
/
&CELL
    cell_dynamics = 'bfgs'
    press = 0.0
/
```

Run, then check relaxed structure in `si_relax.out`.

**Step 6**: Bands + DOS

Bands input (`si_bands.in`):
```
&CONTROL
    calculation = 'bands'
    ...
K_POINTS crystal_b
    5
    0.0 0.0 0.0 20   ! Gamma
    0.5 0.0 0.5 20   ! X
    0.5 0.25 0.75 20 ! W
    0.375 0.375 0.75 20 ! K
    0.0 0.0 0.0 20   ! Gamma
```

```bash
pw.x -in si_bands.in > si_bands.out
bands.x -in si_bands_pp.in > si_bands_pp.out
plotband.x  # interactive
```

### 7.3 ASE Python 接口完整

```python
from ase.build import bulk
from ase.calculators.espresso import Espresso
from ase.io import write, read
import numpy as np

# Si crystal
atoms = bulk('Si', 'diamond', a=5.43)

# Calculator
pseudos = {'Si': 'Si.pbe-n-rrkjus_psl.1.0.0.UPF'}
calc = Espresso(
    pseudopotentials=pseudos,
    kpts=(8, 8, 8),
    input_data={
        'control': {
            'calculation': 'scf',
            'prefix': 'si',
            'pseudo_dir': './pseudo',
            'verbosity': 'high',
            'tprnfor': True,
            'tstress': True,
        },
        'system': {
            'ecutwfc': 50,
            'ecutrho': 400,
            'occupations': 'fixed',
        },
        'electrons': {
            'conv_thr': 1e-10,
            'mixing_beta': 0.7,
        },
    },
)
atoms.calc = calc

# Compute energy + forces
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
stress = atoms.get_stress()

print(f"Energy = {energy:.4f} eV")
print(f"Max force = {np.max(np.abs(forces)):.4f} eV/Å")
print(f"Stress trace = {np.trace(stress.reshape(3,3)):.4f}")
```

### 7.4 Convergence study 自动化

```python
import matplotlib.pyplot as plt
import numpy as np

# ENCUT convergence
ecuts = [20, 30, 40, 50, 60, 80, 100]
energies_E = []

for ecut in ecuts:
    calc.set(input_data={'system': {'ecutwfc': ecut, 'ecutrho': 8*ecut}})
    atoms.calc = calc
    energies_E.append(atoms.get_potential_energy())

# K-point convergence (at converged ECUT)
ks = [(4,4,4), (6,6,6), (8,8,8), (10,10,10), (12,12,12)]
energies_K = []

for k in ks:
    calc.set(kpts=k, input_data={'system': {'ecutwfc': 60, 'ecutrho': 480}})
    atoms.calc = calc
    energies_K.append(atoms.get_potential_energy())

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(ecuts, energies_E, 'o-')
axes[0].set_xlabel('ECUT (Ry)'); axes[0].set_ylabel('E (eV)')
axes[0].set_title('ENCUT convergence')

k_grid = [k[0] for k in ks]
axes[1].plot(k_grid, energies_K, 'o-')
axes[1].set_xlabel('K-grid'); axes[1].set_ylabel('E (eV)')
axes[1].set_title('K-point convergence')

plt.savefig('convergence.png', dpi=200)
```

### 7.5 弹性常数从 stress-strain

```python
import numpy as np
from ase.build import bulk

def compute_elastic_constants_cubic(atoms, calc, strains=[-0.005, 0, 0.005]):
    """For cubic crystals: C11, C12, C44"""
    
    # C11 - uniaxial along x
    C11_data = []
    for s in strains:
        a = atoms.copy()
        cell = a.cell.copy()
        cell[0] *= (1 + s)
        a.set_cell(cell, scale_atoms=True)
        a.calc = calc
        # Get stress
        sigma = a.get_stress()  # Voigt: [σ_xx, σ_yy, σ_zz, σ_yz, σ_xz, σ_xy]
        C11_data.append([s, sigma[0]])
    
    # Fit line
    s_vals, sigmas = zip(*C11_data)
    C11 = np.polyfit(s_vals, sigmas, 1)[0] / -1.602e-19 * 1e21  # to GPa
    
    # Similarly C12 from σ_yy under x-strain
    # C44 from shear strain
    
    return C11

# Run
atoms = bulk('Si', 'diamond', a=5.43)
# ... (with calculator)
C11 = compute_elastic_constants_cubic(atoms, calc)
print(f"C11 = {C11:.1f} GPa (exp: 166 GPa)")
```

### 7.6 Surface energy 完整例

```python
from ase.build import fcc111

def surface_energy(symbol, miller=(1,1,1), n_layers=5, vacuum=15):
    # Bulk reference
    bulk_atoms = bulk(symbol, 'fcc', a=3.615)
    bulk_atoms.calc = calc
    E_bulk = bulk_atoms.get_potential_energy() / len(bulk_atoms)
    
    # Slab
    slab = fcc111(symbol, size=(2, 2, n_layers), vacuum=vacuum)
    slab.calc = calc
    E_slab = slab.get_potential_energy()
    
    # Calculate
    N = len(slab)
    A = slab.cell.lengths()[0] * slab.cell.lengths()[1] * np.sin(np.deg2rad(60))
    
    gamma = (E_slab - N * E_bulk) / (2 * A)  # 2 surfaces
    gamma_si = gamma * 16.022  # eV/Å² to J/m²
    
    return gamma_si

# Cu(111)
gamma = surface_energy('Cu', (1,1,1), n_layers=7, vacuum=15)
print(f"Cu(111) surface energy: {gamma:.2f} J/m²")
# Exp: 1.79 J/m²
```

### 7.7 Phonons with phonopy

```bash
# Step 1: Generate supercell with displacements
phonopy -d --dim "3 3 3"
# Generates POSCAR-001, POSCAR-002, ...

# Step 2: For each displacement, run DFT
for f in POSCAR-*; do
    cp $f POSCAR
    cp INCAR_phonon INCAR
    mpirun vasp_std > log_$f
    cp vasprun.xml vasprun.xml.${f#POSCAR-}
done

# Step 3: Force constants
phonopy -f vasprun.xml.{001..N}

# Step 4: Phonon bands
phonopy --band band.conf
```

`band.conf`:
```
DIM = 3 3 3
BAND = 0 0 0 0.5 0 0.5 0.5 0.25 0.75 0.0 0.0 0.0
BAND_LABELS = $\Gamma$ X K $\Gamma$
FORCE_CONSTANTS = READ
```

### 7.8 习题

**7.1** 安装 QE，跑 H₂ 分子 + 报告键长 + 键能.

**7.2** Si convergence study: ECUT, K-points, supercell size.

**7.3** Cu 弹性常数: compute C11, C12, C44, compare experiment.

**7.4** Cu(111) 表面能 + 比较 layer convergence.

**7.5** Si phonon dispersion with phonopy.

## 第 8 章 高级 DFT 技术

### 8.1 Hybrid functionals 详细

**Exchange分解**:
$$ E_x^{hybrid} = a E_x^{HF} + (1-a) E_x^{DFT} $$

**HSE06** screening:
- Short-range (SR): $\text{erfc}(\omega r)/r$ in Coulomb
- Long-range (LR): $\text{erf}(\omega r)/r$
- 只用 SR 精确交换 → 计算更便宜

**Bandgap 对比** (典型半导体):

| Material | PBE | HSE06 | Exp |
|---|---|---|---|
| Si | 0.65 | 1.17 | 1.17 |
| Ge | 0.0 | 0.78 | 0.74 |
| GaAs | 0.20 | 1.42 | 1.52 |
| SiC | 1.40 | 2.30 | 2.42 |

**问题**: 慢 10×, 对总能改善小，主要给 bandgap.

### 8.2 GW + BSE — 准确多体激发态

**GW approximation**:

$$ \Sigma = i G W $$

- G: Green's function (single particle)
- W: screened Coulomb
- Σ: self-energy

修正 KS 能级 → 准确准粒子能量.

**BSE**: 加电子-空穴相互作用 → 光学性质 (excitons).

**软件**: BerkeleyGW, ABINIT, Yambo.

**Cost**: 100-1000× DFT, 但精度最高 (bandgap ~0.05 eV error).

### 8.3 DFT+U 详细

**Dudarev formalism** (单 effective parameter $U_{eff} = U - J$):

$$ E_{DFT+U} = E_{DFT} + \frac{U_{eff}}{2} \sum_\sigma \text{Tr}[\rho^\sigma (1 - \rho^\sigma)] $$

施加在选定 d/f orbitals.

**Physical meaning**: 阻止 partial occupation, 推向 integer occupation (insulator).

**U 选择方法**:

1. **文献查** — 容易但 not reproducible.
2. **Linear response (Cococcioni)**:

$$ U = \frac{\partial^2 E}{\partial n^2} $$

变 occupation 算 second derivative.

3. **Hybrid 校准**: tune U 使 PBE+U match HSE06.

4. **实验校准**: tune U match bandgap or magnetic moment.

**典型值** (3d transition metals): U = 3-6 eV.

### 8.4 NEB — Nudged Elastic Band 详细

**Goal**: 找化学反应 / 扩散 / 相变的过渡态.

**Algorithm**:
1. Initial structure + final structure
2. Generate N intermediate images (e.g., 7-9)
3. Connect with "elastic band" (springs)
4. Optimize images: each image projects out parallel component of forces

**Climbing image**:
- 最高 image 用 climbing (向上 saddle)
- 其他 images normal NEB

```python
from ase.neb import NEB
from ase.io import read

initial = read('initial.traj')
final = read('final.traj')

# Generate images by interpolation
images = [initial]
for i in range(1, 8):
    img = initial.copy()
    # Linear interpolation
    img.positions = initial.positions + i/8 * (final.positions - initial.positions)
    images.append(img)
images.append(final)

# Setup NEB
neb = NEB(images, climb=True)
neb.interpolate()

# Set calculator for intermediate images
for image in images[1:-1]:
    image.calc = calc

# Optimize
from ase.optimize import BFGS
opt = BFGS(neb, logfile='neb.log')
opt.run(fmax=0.05)

# Energy profile
energies = [img.get_potential_energy() for img in images]
Ea = max(energies) - energies[0]
print(f"Activation barrier: {Ea:.3f} eV")
```

### 8.5 AIMD — Ab initio Molecular Dynamics

**Setup** (VASP):
```
IBRION = 0    # MD
SMASS = 0     # Nose-Hoover thermostat
TEBEG = 300
POTIM = 1.0   # 1 fs
NSW = 5000    # 5 ps
PREC = Low
LREAL = Auto
```

**Output analysis**:
```python
from ase.io import read
import numpy as np

traj = read('XDATCAR', index=':')
positions = np.array([atoms.get_positions() for atoms in traj])

# MSD
msd = np.zeros(len(traj))
for i in range(1, len(traj)):
    diff = positions[i] - positions[0]
    # Account for PBC
    msd[i] = np.mean(np.sum(diff**2, axis=1))

# Diffusion coefficient
# D = MSD / (6 t)
times = np.arange(len(traj)) * 1e-15  # 1 fs steps
from scipy.stats import linregress
slope, *_ = linregress(times[len(times)//2:], msd[len(times)//2:])
D = slope / 6
print(f"D = {D:.3e} m²/s")
```

### 8.6 DFPT — 声子 + 介电

**Linear response**: 对 $V_{ext}$ 一次扰动响应.

Phonon frequencies from dynamical matrix:

$$ D_{IJ} = \frac{1}{\sqrt{M_I M_J}} \frac{\partial^2 E}{\partial R_I \partial R_J} $$

Eigenvalues = $\omega^2$.

**Born effective charges** for LO-TO splitting:

$$ Z^*_{I,\alpha\beta} = \frac{\partial P_\alpha}{\partial R_{I,\beta}} $$

**ph.x in QE**:
```
&inputph
  prefix = 'si'
  outdir = './tmp'
  fildyn = 'si.dyn'
  ldisp = .true.
  nq1 = 4, nq2 = 4, nq3 = 4
  tr2_ph = 1.0d-14
/
```

### 8.7 TDDFT — Time-dependent

For excited states + optical properties:

**TDDFT** in linear response:

$$ \left[\begin{array}{cc}A & B \\ B^* & A^*\end{array}\right]\left[\begin{array}{c}X \\ Y\end{array}\right] = \omega\left[\begin{array}{cc}1 & 0 \\ 0 & -1\end{array}\right]\left[\begin{array}{c}X \\ Y\end{array}\right] $$

Gives excitation energies + oscillator strengths.

**Real-time TDDFT**: 解 time-dependent KS 方程数值.

### 8.8 习题

**8.1** Compare PBE vs SCAN vs HSE06 for ZnO bandgap.

**8.2** Find U value for NiO using linear response.

**8.3** NEB for H diffusion in Pd FCC (between octahedral sites).

**8.4** AIMD for liquid Si at 1800 K, compute RDF + diffusion.

**8.5** Phonon dispersion for Si using DFPT, identify LO-TO splitting.

## 第 9 章 DFT → 下游接口

### 9.1 DFT → CALPHAD endmember G

**算 0K 形成焓**:

```python
import numpy as np

def formation_enthalpy_DFT(compound_DFT, elements_DFT, stoichiometry):
    """
    H_f = E(compound) - Σ x_i E(element_i)
    Per atom.
    """
    E_compound = compound_DFT.get_potential_energy() / len(compound_DFT)
    
    H_f = E_compound
    for elem, x in zip(elements_DFT, stoichiometry):
        E_elem = elem.get_potential_energy() / len(elem)
        H_f -= x * E_elem
    
    return H_f  # eV/atom

# Example: NaCl
H_f_NaCl = formation_enthalpy_DFT(nacl_atoms, [na_atoms, cl_atoms], [0.5, 0.5])
print(f"H_f(NaCl) = {H_f_NaCl * 96.485:.1f} kJ/mol")
# Exp: -411 kJ/mol
```

**温度 correction**:

```python
def temperature_correction(atoms, T, phonon_calc):
    """
    G(T) = E(0K) + ZPE + integrated F_vib(T)
    """
    omegas = phonon_calc.get_frequencies()  # cm^-1
    omegas = omegas[omegas > 0]  # exclude imaginary
    
    hbar = 6.582e-16  # eV·s
    k_B = 8.617e-5  # eV/K
    c = 3e10  # cm/s
    
    # Convert cm^-1 to angular frequency
    omegas_rad = omegas * 2 * np.pi * c
    
    # ZPE
    ZPE = 0.5 * np.sum(hbar * omegas_rad)  # in eV
    
    # F_vib at T
    F_vib = 0
    for omega in omegas_rad:
        x = hbar * omega / (k_B * T)
        F_vib += k_B * T * np.log(1 - np.exp(-x))
    
    G = atoms.get_potential_energy() + ZPE + F_vib
    return G

# Now fit G(T) to CALPHAD polynomial form
```

### 9.2 DFT → MLIP training data

**Format**: extended XYZ (extxyz).

```python
from ase.io import read, write

# Collect DFT trajectories
all_atoms = []
for outcar_file in glob.glob("*/OUTCAR"):
    traj = read(outcar_file, index=':')  # all SCF/relax steps
    
    # Filter: meaningful configurations
    for atoms in traj:
        if not (atoms.get_potential_energy() and atoms.get_forces() is not None):
            continue
        # Optional: check force magnitudes (avoid unconverged)
        max_force = np.max(np.abs(atoms.get_forces()))
        if max_force > 50:  # eV/Å (likely unconverged)
            continue
        
        # Add metadata
        atoms.info['energy'] = atoms.get_potential_energy()
        atoms.info['stress'] = atoms.get_stress(voigt=False)
        atoms.arrays['forces'] = atoms.get_forces()
        
        all_atoms.append(atoms)

print(f"Total configurations: {len(all_atoms)}")

# Save
write('dft_data.xyz', all_atoms)
```

**Data balance**:
- Equilibrium: ~30%
- Perturbed: ~30%
- High-T snapshots: ~20%
- Defective: ~10%
- Surface/interface: ~10%

### 9.3 DFT → CP-FEM 弹性 + slip system

```python
# Elastic constants → DAMASK material file
import yaml

elastic = {
    'phase': 'FCC_HEA',
    'lattice': 'cF',
    'mechanical': {
        'elastic': {
            'type': 'Hooke',
            'C_11': float(C11 * 1e9),  # Pa
            'C_12': float(C12 * 1e9),
            'C_44': float(C44 * 1e9),
        },
        'plastic': {
            'type': 'phenopowerlaw',
            'N_sl': [12],
            'xi_0_sl': [tau_0 * 1e6],  # MPa to Pa
            # ... from MD
        }
    }
}

with open('material.yaml', 'w') as f:
    yaml.dump(elastic, f)
```

### 9.4 实战 — DFT 数据 → CALPHAD database

完整 workflow:

```python
def dft_to_calphad_endmember(element, structure, T_range=[300, 1000, 1500]):
    """Convert DFT data to CALPHAD G(T) parameters"""
    
    # 1. Compute E_0 at relaxed structure
    atoms = bulk(element, structure)
    atoms.calc = vasp_calc
    opt = BFGS(atoms)
    opt.run(fmax=0.001)
    E_0 = atoms.get_potential_energy() / len(atoms)
    
    # 2. Compute phonons
    phonons = compute_phonons(atoms, supercell=(3,3,3))
    
    # 3. Free energy at each T
    G_T = []
    for T in T_range:
        ZPE = compute_ZPE(phonons)
        F_vib = compute_F_vib(phonons, T)
        G = E_0 + ZPE + F_vib
        G_T.append((T, G))
    
    # 4. Fit to SGTE form
    # G(T) = a + b*T + c*T*ln(T) + d*T^2 + e/T
    from scipy.optimize import curve_fit
    
    def sgte_form(T, a, b, c, d, e):
        return a + b*T + c*T*np.log(T) + d*T**2 + e/T
    
    T_vals = np.array([t for t, g in G_T])
    G_vals = np.array([g for t, g in G_T]) * 96485  # eV to J/mol
    
    popt, _ = curve_fit(sgte_form, T_vals, G_vals)
    
    # 5. Write to TDB
    tdb_text = f"FUNCTION G_{element}_{structure} 298.15 \n"
    tdb_text += f"  {popt[0]:.4f} + {popt[1]:.4f}*T + {popt[2]:.4f}*T*LN(T) \n"
    tdb_text += f"  + {popt[3]:.4e}*T**2 + {popt[4]:.4e}/T; 6000 N !\n"
    
    return tdb_text

# Example: Fe BCC
tdb_Fe = dft_to_calphad_endmember('Fe', 'bcc')
print(tdb_Fe)
```

### 9.5 习题

**9.1** DFT 算 NaCl + correction → 比较 -411 kJ/mol 实验.

**9.2** Build extxyz file from VASP OUTCAR.

**9.3** Fit DFT phonon data → SGTE polynomial.

**9.4** Compare PBE 与 SCAN endmember values.

**9.5** Multi-fidelity: combine DFT + experiment for end-member.

---


