# 第三篇 · 任脉第 2 步：原子层 — MD + MLIP

*上游：第二篇 DFT 提供训练数据 + 验证标准*
*下游：CALPHAD 借助 MD 算出迁移性、扩散系数；Phase-field 借助 MLIP 算原子尺度过程*

## 第 10 章 MD 基础

### 10.1 经典力学回顾

**Hamilton equations**:

$$ \dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i} $$

For N atoms:

$$ H = \sum_i \frac{p_i^2}{2 m_i} + V(\{q_i\}) $$

**Newton's equation** (eliminate p):

$$ m_i \ddot{q}_i = -\nabla_i V = F_i $$

### 10.2 数值积分 algorithms

**Velocity-Verlet** (most common):

$$ q_i(t + \Delta t) = q_i(t) + v_i(t) \Delta t + \frac{1}{2} \frac{F_i(t)}{m_i} \Delta t^2 $$

$$ v_i(t + \Delta t) = v_i(t) + \frac{F_i(t) + F_i(t + \Delta t)}{2 m_i} \Delta t $$

**Properties**:
- Symplectic (energy 长期守恒)
- 2nd order accurate
- Reversible

**Leapfrog**:

$$ v(t + \Delta t/2) = v(t - \Delta t/2) + F(t)/m \Delta t $$

$$ q(t + \Delta t) = q(t) + v(t + \Delta t/2) \Delta t $$

Equivalent to Velocity-Verlet (offset half-step).

**Higher order**: Gear predictor-corrector (4th-7th), 但 not symplectic.

### 10.3 系综理论

**NVE (microcanonical)**:
- Hamiltonian = const → E conserved
- Natural MD output
- 用于 equilibrium properties

**NVT (canonical)**:
- Coupled to "heat bath" at T
- 需要 thermostat

**Thermostats**:

**Berendsen** (rescale velocities):
$$ v_i \to v_i \sqrt{1 + \frac{\Delta t}{\tau}(\frac{T_{target}}{T} - 1)} $$

Fast but **not canonical** ensemble (no fluctuations correct).

**Nose-Hoover**:

Extended system with extra DOF $\xi$:

$$ \ddot{q}_i = F_i/m_i - \xi \dot{q}_i $$

$$ \dot{\xi} = (\sum_i m_i v_i^2 - g k_B T) / Q $$

Gives **true canonical**.

**Langevin**:

$$ m_i \ddot{q}_i = F_i - \gamma m_i \dot{q}_i + R_i(t) $$

with $R_i$ random force:
$$ \langle R_i(t) R_j(t') \rangle = 2 \gamma m_i k_B T \delta_{ij} \delta(t-t') $$

Stochastic but exact canonical.

**NPT** (Parrinello-Rahman): also barostat:

$$ \dot{h} = V \dot{h}^{-T} (\Sigma - P I) / Q_h $$

cell h variable + extra DOFs.

### 10.4 长程力 — Ewald summation

Coulomb $V = q_i q_j / r$ in periodic system:

$$ U_{Ewald} = U_{real} + U_{reciprocal} + U_{self} $$

Real space (短程):
$$ U_{real} = \frac{1}{2}\sum_{ij,n}^{'} \frac{q_i q_j}{|r_{ij} + n L|}\text{erfc}(\alpha |r_{ij}+nL|) $$

Reciprocal (Fourier 长程):
$$ U_{rec} = \frac{2\pi}{V}\sum_{k \neq 0}\frac{\exp(-k^2/(4\alpha^2))}{k^2} |\rho(k)|^2 $$

**PPPM (Particle-Particle-Particle-Mesh)** = Ewald 改良，O(N log N).

### 10.5 周期边界条件 + minimum image

```python
def minimum_image(r1, r2, cell):
    """Periodic boundary minimum image convention"""
    dr = r2 - r1
    dr = dr - cell * np.round(dr / cell)
    return dr
```

### 10.6 动力学 properties

**RDF**:
```python
def compute_rdf(positions, cell, dr=0.1, rmax=10):
    n_atoms = len(positions)
    n_bins = int(rmax / dr)
    rdf = np.zeros(n_bins)
    
    for i in range(n_atoms):
        for j in range(i+1, n_atoms):
            d = np.linalg.norm(minimum_image(positions[i], positions[j], cell))
            if d < rmax:
                bin_idx = int(d / dr)
                rdf[bin_idx] += 2  # i-j and j-i
    
    # Normalize
    rho = n_atoms / np.prod(cell)
    for i in range(n_bins):
        r = (i + 0.5) * dr
        shell_volume = 4 * np.pi * r**2 * dr
        rdf[i] /= (n_atoms * rho * shell_volume)
    
    return rdf
```

**MSD + Diffusion**:
```python
def compute_msd(trajectory, cell):
    """MSD with PBC unwrapping"""
    positions = np.array([atoms.get_positions() for atoms in trajectory])
    n_frames, n_atoms, _ = positions.shape
    
    # Unwrap (subtract drift)
    com = np.mean(positions, axis=1, keepdims=True)
    positions -= com  # remove COM motion
    
    msd = np.zeros(n_frames)
    for t in range(1, n_frames):
        diff = positions[t] - positions[0]
        msd[t] = np.mean(np.sum(diff**2, axis=1))
    
    return msd

# D = slope of MSD / 6 in 3D
```

### 10.7 LAMMPS 完整 input

```bash
# in.lammps
units metal
atom_style atomic
boundary p p p

# 体系
lattice fcc 3.615
region box block 0 10 0 10 0 10
create_box 1 box
create_atoms 1 box

# 势函数
pair_style eam/alloy
pair_coeff * * Cu.eam.alloy Cu

# 初始化
mass 1 63.55
velocity all create 300.0 12345

# 平衡 NVT
fix 1 all nvt temp 300 300 0.1
timestep 1.0e-3  # 1 fs
run 10000

# 生产 NVE
unfix 1
fix 2 all nve
dump 1 all custom 100 dump.lammpstrj id type x y z

# 计算 RDF
compute rdf all rdf 100
fix rdfprint all ave/time 10 10 100 c_rdf[*] file rdf.txt mode vector

run 100000

# Diffusion
compute msd all msd
fix msdprint all ave/time 10 10 100 c_msd[1] c_msd[2] c_msd[3] file msd.txt
```

### 10.8 习题

**10.1** 推导 Velocity-Verlet from Taylor expansion.

**10.2** 实现 Berendsen vs Nose-Hoover thermostat, compare T fluctuations.

**10.3** RDF for liquid Ar, find first peak.

**10.4** MSD → D for liquid metal, check Arrhenius vs T.

**10.5** Setup PPPM for ionic system (e.g., NaCl liquid).

## 第 11 章 势函数全谱

### 11.1 Pair potentials

**Lennard-Jones**:
- 2 parameters: σ (size), ε (depth)
- 不错 for noble gases
- 用 cutoff (e.g., 2.5 σ)

**Buckingham**:
$$ V = A e^{-r/\rho} - C/r^6 $$
更好 for ionic crystals.

**Morse**:
$$ V = D_e (e^{-2a(r-r_e)} - 2 e^{-a(r-r_e)}) $$
分子键, has equilibrium $r_e$.

### 11.2 Many-body potentials

**EAM (Embedded Atom Method)**:

$$ E_i = F(\rho_i) + \frac{1}{2}\sum_j \phi(r_{ij}) $$

**Physical**: 原子 embedded in 电子云 $\rho_i$.

For Cu (Mishin et al. 2001):
- F(ρ): tabulated, ~ -sqrt(ρ)
- φ(r): repulsive at small r, attractive intermediate, 0 at cutoff

**MEAM (Modified EAM)**:
- 加角度依赖（covalent contribution）
- 适合 HCP, BCC (Mg, Ti)

**Tersoff** (covalent):

$$ V = f_R(r) - b_{ij} f_A(r) $$

with bond order $b_{ij}$ depending on local environment.

**Stillinger-Weber** for Si:
$$ V = \sum_{ij} V_2(r_{ij}) + \sum_{ijk} V_3(r_{ij}, r_{ik}, \theta_{ijk}) $$

3-body terms favor tetrahedral angle.

### 11.3 Reactive potentials

**ReaxFF** (Reactive Force Field):
- Bond order based
- Can break/form bonds
- 复杂参数 (~50 per element pair)
- 慢 100× than EAM

**COMB3**: Multi-element charge-equilibration ReaxFF.

**AIREBO**: For hydrocarbons.

### 11.4 ML potentials — generations

**Generation 1 (2007-2012)**: 
- Behler-Parrinello NN potentials
- High-Dimensional NN (HDNNP)
- 用 symmetry functions (ACSF)

**Generation 2 (2013-2020)**:
- GAP (Gaussian Approximation Potential, Bartók 2010)
- SOAP descriptor
- Linear models (MTP)
- DeepMD-kit (Wang 2018)

**Generation 3 (2020+)**:
- **Equivariant GNN**: NequIP, Allegro, MACE
- Higher-order tensor messages
- SOTA 精度
- Universal models (MACE-MP-0)

### 11.5 Descriptor 详细

**SOAP (Smooth Overlap of Atomic Positions)**:

$$ \rho_i(r) = \sum_j e^{-\alpha (r - r_{ij})^2} $$

Project on basis:
$$ c_{nlm}^i = \int \rho_i(r) g_n(r) Y_{lm}(\hat{r}) dr $$

**SOAP descriptor**:
$$ p_{n_1 n_2 l}^i = \sum_m c_{n_1 lm}^{i*} c_{n_2 lm}^i $$

Rotation invariant.

**ACSF (Atom-Centered Symmetry Functions)** (Behler):

$$ G_i^{(2)} = \sum_j e^{-\eta(r_{ij}-r_s)^2} f_c(r_{ij}) $$

$$ G_i^{(5)} = 2^{1-\zeta}\sum_{j,k} (1+\lambda \cos\theta)^\zeta e^{-\eta(r_{ij}^2+r_{ik}^2+r_{jk}^2)} f_c f_c f_c $$

### 11.6 MACE architecture detail

**Equivariant tensor**: l = 0, 1, 2 features.

**Message passing**:

$$ m_i^{(t)} = \sum_{j \in N(i)} \text{TP}(h_i^{(t-1)}, h_j^{(t-1)}, Y(r_{ij})) $$

with TP = tensor product, Y = spherical harmonics.

**Output**: scalar energy + vector forces.

### 11.7 习题

**11.1** 实现 LJ pair potential for Ar liquid.

**11.2** Use EAM for Cu, compare bulk modulus to DFT.

**11.3** Train simple linear MLP on H2O dataset.

**11.4** Compare DeepMD vs MACE on Cantor HEA.

**11.5** Compute SOAP descriptor for Si crystal vs amorphous.

## 第 12 章 MACE-MP-0 实战

### 12.1 完整 install + setup

```bash
# Create env
conda create -n mace python=3.11
conda activate mace

# PyTorch with CUDA (GPU 推荐 A100/H100/RTX 4090)
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# MACE
pip install mace-torch

# Visualization + analysis
pip install ase pymatgen ovito-python

# Test
python -c "from mace.calculators import mace_mp; print('MACE OK')"
```

**Download model** (auto first time, ~1-2 GB):

```python
from mace.calculators import mace_mp
calc = mace_mp("medium")  # downloads to ~/.cache/mace
```

### 12.2 5 minute quickstart

```python
from mace.calculators import mace_mp
from ase.build import bulk

calc = mace_mp("medium", device="cuda")

# Cu
atoms = bulk("Cu", "fcc", a=3.615) * (4, 4, 4)
atoms.calc = calc

energy = atoms.get_potential_energy()
forces = atoms.get_forces()
stress = atoms.get_stress()

print(f"256 atom Cu energy: {energy:.4f} eV")
print(f"E/atom: {energy/len(atoms):.6f} eV/atom")
print(f"Stress: {stress}")
```

### 12.3 大体系 MD (10000 atoms)

```python
import numpy as np
from ase.md.npt import NPT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units

# 10x10x10 supercell of Fe BCC = 2000 atoms
atoms = bulk("Fe", "bcc", a=2.87) * (10, 10, 10)
atoms.calc = mace_mp("medium", device="cuda")

# Initialize velocities
MaxwellBoltzmannDistribution(atoms, temperature_K=300)

# NPT dynamics
ttime = 25 * units.fs  # thermostat coupling
ptime = 1000 * units.fs  # barostat coupling
pfactor = (ptime**2) * 100 * units.GPa  # barostat factor

dyn = NPT(
    atoms,
    timestep=2 * units.fs,
    temperature_K=300,
    externalstress=0,  # zero pressure
    ttime=ttime,
    pfactor=pfactor,
)

# Track properties
energies = []
temperatures = []
pressures = []
volumes = []

def log():
    energies.append(atoms.get_total_energy())
    temperatures.append(atoms.get_temperature())
    p = -np.trace(atoms.get_stress(voigt=False)) / 3 * 1e-9  # Pa to GPa
    pressures.append(p)
    volumes.append(atoms.get_volume())

dyn.attach(log, interval=100)

# Run 100 ps
dyn.run(50000)  # 100 ps at 2 fs

# Analysis
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0,0].plot(np.array(energies) - energies[0])
axes[0,0].set_title('Energy drift')
axes[0,1].plot(temperatures)
axes[0,1].set_title('Temperature')
axes[1,0].plot(pressures)
axes[1,0].set_title('Pressure')
axes[1,1].plot(volumes)
axes[1,1].set_title('Volume')
plt.savefig('MD_diagnostics.png')
```

### 12.4 Phonon spectra with MACE-MP-0

```python
import phonopy
from phonopy.interface.ase import get_phonopy_atoms

# Convert to phonopy
ph_atoms = get_phonopy_atoms(atoms)

# Compute force constants
phonon = phonopy.Phonopy(ph_atoms, supercell_matrix=[[3,0,0],[0,3,0],[0,0,3]])
phonon.generate_displacements(distance=0.01)

# For each displaced supercell, compute forces with MACE-MP-0
supercells = phonon.supercells_with_displacements
forces_array = []
for sc in supercells:
    sc.calc = mace_mp("medium")
    forces = sc.get_forces()
    forces_array.append(forces)

phonon.set_forces(forces_array)
phonon.produce_force_constants()

# Phonon bands
phonon.run_band_structure([[0,0,0],[0.5,0,0],[0.5,0.5,0],[0,0,0]])
phonon.write_yaml_band_structure()
```

### 12.5 Elastic constants automated

```python
from ase.calculators.calculator import all_changes

def compute_C11_C12_C44(atoms, calc, strain=0.005, n_points=5):
    """Cubic crystal elastic constants"""
    # Reference (relaxed)
    atoms.calc = calc
    from ase.optimize import BFGS
    BFGS(atoms).run(fmax=0.001)
    
    strains = np.linspace(-strain, strain, n_points)
    
    # C11: uniaxial along x
    sigma_xx_data = []
    for s in strains:
        a = atoms.copy()
        cell = a.cell.copy()
        cell[0,0] *= (1 + s)
        a.set_cell(cell, scale_atoms=True)
        a.calc = calc
        sigma = a.get_stress(voigt=False)
        sigma_xx_data.append(sigma[0,0])
    
    # Fit: σ_xx = C11 * ε_xx (under just ε_xx, others zero ↔ this gives effective)
    # More rigorous: use full elastic tensor
    C11 = -np.polyfit(strains, sigma_xx_data, 1)[0] / 1e9
    
    # Similarly for C44 (shear)
    sigma_xy_data = []
    for s in strains:
        a = atoms.copy()
        # Shear strain
        cell = a.cell.copy()
        cell[1,0] = s * cell[1,1]  # tilt y
        a.set_cell(cell, scale_atoms=True)
        a.calc = calc
        sigma = a.get_stress(voigt=False)
        sigma_xy_data.append(sigma[0,1])
    
    C44 = -np.polyfit(strains, sigma_xy_data, 1)[0] / 1e9
    
    return C11, C44

# Run on Cu
atoms = bulk("Cu", "fcc", a=3.615)
calc = mace_mp("medium")
C11, C44 = compute_C11_C12_C44(atoms, calc)
print(f"Cu: C11 = {C11:.0f} GPa, C44 = {C44:.0f} GPa")
# Exp: C11=168, C44=75
```

### 12.6 High-throughput screening with MACE-MP-0

```python
import pandas as pd
import numpy as np
from itertools import combinations
from ase.build import bulk

# 10 elements
elements = ["Cu", "Ni", "Co", "Fe", "Mn", "Cr", "V", "Ti", "Al", "Mg"]

# Generate all binary compositions FCC (50-50)
results = []

for e1, e2 in combinations(elements, 2):
    try:
        # 50-50 alloy
        a_avg = (bulk(e1).cell.lengths()[0] + bulk(e2).cell.lengths()[0]) / 2
        atoms = bulk(e1, "fcc", a=a_avg) * (3, 3, 3)
        
        # Alternate
        for i in range(0, len(atoms), 2):
            atoms.symbols[i] = e2
        
        atoms.calc = mace_mp("medium")
        
        from ase.optimize import BFGS
        BFGS(atoms).run(fmax=0.05, steps=50)
        
        E = atoms.get_potential_energy() / len(atoms)
        a_opt = atoms.cell.lengths()[0] / 3
        
        results.append({
            'e1': e1, 'e2': e2,
            'E_per_atom': E,
            'lattice': a_opt
        })
        
        print(f"{e1}-{e2}: E = {E:.4f} eV/atom")
    
    except Exception as ex:
        print(f"Failed {e1}-{e2}: {ex}")

df = pd.DataFrame(results)
df.sort_values('E_per_atom').to_csv('binary_screen.csv')
print(f"\nScreened {len(df)} binaries in ~30 minutes on GPU")
```

### 12.7 习题

**12.1** 安装 MACE-MP-0 + 跑 100-atom Cu MD 100 ps.

**12.2** Phonon dispersion for Si with MACE-MP-0 vs DFT.

**12.3** Elastic constants for HEA, validate against DFT (5 random samples).

**12.4** Diffusion coefficient for Cu vacancy at 1000 K.

**12.5** Screen 100 binary alloys for cohesive energy ranking.

## 第 13 章 自训 MLIP

### 13.1 数据准备策略

**Diversity is key**.

**Recipe** for typical material:
- 30%: Equilibrium 结构（多 cell volumes）
- 25%: Perturbed atomic positions (0.1-0.5 Å)
- 20%: AIMD snapshots at 多个 T
- 15%: Defective configurations
- 10%: Surfaces / interfaces

**Active learning** generates data iteratively (better):

```python
def active_learning(initial_data, n_iter=10, dft_calc=None, target_uncertainty=0.05):
    train_data = initial_data
    
    for iteration in range(n_iter):
        print(f"\n=== Iteration {iteration} ===")
        
        # Train MLIP
        mlip = train_mace(train_data, config="medium")
        
        # Train ensemble (5 different seeds)
        ensemble = [train_mace(train_data, seed=i) for i in range(5)]
        
        # MD with one MLIP
        traj = run_md(mlip, T=300, n_steps=10000)
        
        # Compute uncertainty for each snapshot
        snapshots = sample_trajectory(traj, n=20)
        uncertainties = []
        for snap in snapshots:
            E_ensemble = [m.calculate_energy(snap) for m in ensemble]
            uncertainties.append(np.std(E_ensemble))
        
        print(f"Max uncertainty: {max(uncertainties)*1000:.1f} meV/atom")
        
        if max(uncertainties) < target_uncertainty:
            print("Converged!")
            break
        
        # Select highest-uncertainty for DFT
        high_unc_indices = np.argsort(uncertainties)[-5:]
        new_configs = [snapshots[i] for i in high_unc_indices]
        
        # Run DFT
        new_dft = [dft_calc.compute(c) for c in new_configs]
        
        # Add to training
        train_data.extend(new_dft)
        print(f"Added {len(new_dft)} new configurations")
    
    return mlip
```

### 13.2 MACE training detailed

`config.yaml`:

```yaml
# Output naming
name: my_mace_v1

# Hardware
device: cuda
default_dtype: float32

# Data files
train_file: train.xyz
valid_file: valid.xyz
test_file: test.xyz

# Model architecture
model: MACE
r_max: 5.0           # cutoff radius (Å)
num_basis: 8          # radial basis
max_ell: 3            # max spherical harmonic degree
correlation: 3        # message passing depth (3 is good)
hidden_irreps: "256x0e + 256x1o"  # scalar + vector features

# Optimizer
batch_size: 8
max_num_epochs: 200
learning_rate: 0.001
scheduler_patience: 50
weight_decay: 5.0e-7
ema: true
ema_decay: 0.99

# Loss weights
loss: weighted        # energy + force + stress
energy_weight: 1.0
forces_weight: 100.0
stress_weight: 100.0

# Foundation (optional - fine-tuning)
# foundation_model: medium  # use to fine-tune MACE-MP-0
```

**Train**:

```bash
mace_run_train --config config.yaml
```

**Output**: `my_mace_v1_swa.model` (smoothed weights averaging - 最稳).

### 13.3 LAMMPS deployment

```bash
# Build LAMMPS with MACE
cd lammps
make yes-ml-mace
make mpi

# In LAMMPS input
pair_style mace
pair_coeff * * my_mace_v1_swa.model Fe Cr Ni
```

**Speed comparison** (typical):
- EAM: 10⁵ atom·ns/day/GPU
- MACE: 10³ atom·ns/day/GPU (100× slower than EAM)
- AIMD: 10⁻¹ atom·ns/day (10⁵× slower than MACE)

→ MACE 是 EAM 与 AIMD 的 sweet spot.

### 13.4 Validation 严谨

```python
import numpy as np
from ase.io import read

# Load test set
test_atoms = read("test.xyz", index=":")

# Compute MLIP predictions
mlip = load_mace("my_mace_v1_swa.model")
errors_E = []
errors_F = []

for atoms in test_atoms:
    # MLIP
    atoms_copy = atoms.copy()
    atoms_copy.calc = mlip
    E_mlip = atoms_copy.get_potential_energy()
    F_mlip = atoms_copy.get_forces()
    
    # DFT (from file)
    E_dft = atoms.info['energy']
    F_dft = atoms.arrays['forces']
    
    errors_E.append((E_mlip - E_dft) / len(atoms) * 1000)  # meV/atom
    errors_F.append(F_mlip - F_dft)

# Statistics
errors_E = np.array(errors_E)
errors_F = np.concatenate(errors_F, axis=0)

print(f"Energy MAE: {np.mean(np.abs(errors_E)):.2f} meV/atom")
print(f"Energy RMSE: {np.sqrt(np.mean(errors_E**2)):.2f} meV/atom")
print(f"Force MAE: {np.mean(np.abs(errors_F))*1000:.2f} meV/Å")
print(f"Force RMSE: {np.sqrt(np.mean(errors_F**2))*1000:.2f} meV/Å")
```

**Acceptance criteria**:
- Energy: < 5 meV/atom (excellent), < 10 (good)
- Force: < 50 meV/Å (excellent), < 100 (good)

### 13.5 Real example — Fe-Cr-Ni HEA potential

**Workflow** (your CALPHAD background expertise!):

```
1. Generate diverse Fe-Cr-Ni configurations (SQS, defects, surfaces)
2. DFT calculations (VASP/QE PBE+D3)
3. Train MACE
4. Active learning loop
5. Validate at: 
   - Lattice constants
   - Elastic constants
   - Phonon stability
   - Surface energy
   - σ phase formation (CALPHAD prediction!)
6. Deploy: 10⁵ atom MD studies
```

### 13.6 习题

**13.1** Active learning: 10 iterations, plot uncertainty convergence.

**13.2** Train MACE on Cu-Zr metallic glass (1000 configs).

**13.3** Compare DeepMD vs MACE training time + final precision.

**13.4** Deploy trained MACE in LAMMPS, run 100 ns MD.

**13.5** Multi-MLP ensemble (5 MACEs) for UQ.

---

# v3 扩展总结

**新增页数**: ~50 页 (Part 2 + Part 3 深化)

**新增内容**:
- 详细 DFT 公式推导
- HK + KS + SCF 完整说明
- 9 章 / 章 都有完整代码
- Phonon, NEB, AIMD, DFPT 详细
- DFT → CALPHAD / MLIP / CP-FEM 自动化 code
- MD 系综理论 + thermostats
- 势函数 generations (LJ → EAM → MACE)
- MACE-MP-0 + active learning 完整 workflow

**v3 总页数预估**: ~150 页 (v2 的 ~80 + 新增 ~70)

**还需要扩展**:
- Round 3: Part 7 (ML) + Part 8 (BO+MC) 深化 → ~210 页
- Round 4: 表征 + 完整案例 + ICME → ~260 页
- Round 5: 习题大全 + 答案 + 附录 → 300+ 页

---

*Li Zhou · v3 第二轮扩展 · 2026.06*


