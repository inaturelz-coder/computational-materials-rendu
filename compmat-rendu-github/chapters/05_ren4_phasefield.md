# 第五篇 · 任脉第 4 步：介观层 — Phase-field

*上游：CALPHAD 提供热力学；MD/MLIP 提供原子尺度参数；DFT 提供界面能、形成能*
*下游：CP-FEM 用 Phase-field 输出的微观组织作为初始构型*

## 第 19 章 相场理论基础

### 19.1 哲学起源

**Diffuse interface vs Sharp interface**:

| 角度 | Sharp interface | Diffuse interface (phase-field) |
|---|---|---|
| 数学 | Free boundary problem | PDE |
| 数值 | 复杂（tracking）| 标准 PDE solver |
| 物理 | 界面厚度 = 0 | 界面厚度 = ξ |
| 拓扑 | 难处理（合并/分裂）| 自然 |

**Phase-field 范式**：用 smooth field 描述 microstructure，避开 explicit interface tracking.

### 19.2 Ginzburg-Landau theory

**Original GL** for superconductors (1950)，但 framework 通用:

$$ F[\phi] = \int_V \left[ f(\phi) + \frac{1}{2}\kappa|\nabla \phi|^2 + ... \right] dV $$

- $f(\phi)$: 局部自由能
- $\frac{\kappa}{2}|\nabla\phi|^2$: 梯度（界面）能量
- $\kappa$: gradient coefficient

### 19.3 双井势 — physical meaning

**Standard double-well**:

$$ f_{DW}(\phi) = W \phi^2 (1-\phi)^2 $$

- Minima at $\phi = 0, 1$
- Barrier height $W/16$ at $\phi = 0.5$

**Interface profile** (1D, equilibrium):

$$ \phi(x) = \frac{1}{2}\left[1 + \tanh\left(\frac{x}{\sqrt{2\kappa/W}}\right)\right] $$

**Interface width**:
$$ \xi \approx \sqrt{\frac{2\kappa}{W}} $$

**Interface energy**:
$$ \gamma = \frac{1}{3}\sqrt{2 \kappa W} $$

### 19.4 Derivation: Allen-Cahn from variational principle

非守恒 order parameter (e.g., orientation, phase type):

**Linear law of irreversible thermodynamics**:

$$ \frac{\partial \phi}{\partial t} = -M \frac{\delta F}{\delta \phi} $$

Functional derivative:

$$ \frac{\delta F}{\delta \phi} = \frac{\partial f}{\partial \phi} - \kappa \nabla^2 \phi $$

So:

$$ \boxed{\frac{\partial \phi}{\partial t} = -M\left(\frac{\partial f}{\partial \phi} - \kappa \nabla^2 \phi\right)} $$

### 19.5 Derivation: Cahn-Hilliard from mass conservation

Conserved field (e.g., concentration):

$$ \frac{\partial c}{\partial t} + \nabla \cdot J = 0 $$

with Fick-like law:

$$ J = -M \nabla \mu = -M \nabla \frac{\delta F}{\delta c} $$

Combine:

$$ \boxed{\frac{\partial c}{\partial t} = \nabla \cdot \left( M \nabla \frac{\delta F}{\delta c} \right) = \nabla \cdot M \nabla \left(\frac{\partial f}{\partial c} - \kappa \nabla^2 c\right)} $$

**Note**: 4th order in space — harder numerically.

### 19.6 Sharp interface limit

When $\xi \to 0$, phase-field recovers sharp interface physics:
- Gibbs-Thomson effect: $\Delta T = \Gamma \kappa$ (curvature)
- Stefan condition: $L \dot{n} = k_s \nabla T_s - k_l \nabla T_l$
- Mass conservation at interface

**Matched asymptotic expansion** rigorously derives this.

### 19.7 习题

**19.1**: Derive Allen-Cahn 详细 from F minimization.

**19.2**: Show interface profile is tanh-shape.

**19.3**: Compute γ for given W, κ.

**19.4**: Why Cahn-Hilliard is 4th order while Allen-Cahn is 2nd?

**19.5**: Discretize 1D Allen-Cahn with finite difference.

## 第 20 章 相场方程

### 20.1 Multi-phase formulations

**Steinbach multi-phase field** (1996):

$$ \frac{\partial \phi_\alpha}{\partial t} = -\sum_\beta M_{\alpha\beta} \left( \frac{\delta F}{\delta \phi_\alpha} - \frac{\delta F}{\delta \phi_\beta} \right) $$

with constraint $\sum_\alpha \phi_\alpha = 1$ enforced.

**Number of equations**: N - 1 (one redundant).

**Folch-Plapp formulation**:

Alternative formulation with thin interface limit + quantitative accuracy.

### 20.2 Anti-trapping flux

For quantitative solidification:

$$ J^{at} = -a(\phi) \dot{\phi} W \hat{n} \Delta c $$

Prevents spurious solute trapping at interface.

### 20.3 Elastic coupling — Eshelby

Misfit strain (precipitate vs matrix):

$$ \epsilon^*_{ij}(\phi) = \phi \cdot \epsilon^*_{ij}^{precipitate} $$

Add elastic energy:

$$ F_{el} = \frac{1}{2} \int C_{ijkl} \left[\epsilon_{ij} - \epsilon^*_{ij}\right] \left[\epsilon_{kl} - \epsilon^*_{kl}\right] dV $$

**Solve mechanical equilibrium** simultaneously:

$$ \nabla \cdot \sigma = 0 $$

with $\sigma_{ij} = C_{ijkl}(\epsilon_{kl} - \epsilon^*_{kl})$.

**Outcome**: precipitate shapes (rods, plates, cubes) from elastic minimization.

### 20.4 Temperature coupling

Heat equation:

$$ \rho C_p \frac{\partial T}{\partial t} = \nabla \cdot (k \nabla T) + L \frac{\partial \phi}{\partial t} $$

- L: latent heat
- k: thermal conductivity
- Coupled to phase-field via $\Delta T$ at interface

### 20.5 KKS model — quantitative chemical PF

**Kim-Kim-Suzuki (KKS)**:

Define phase-specific compositions $c_\alpha, c_\beta$ such that:

$$ c = h(\phi) c_\beta + (1 - h(\phi)) c_\alpha $$

with $h(\phi) = \phi^3(10 - 15\phi + 6\phi^2)$ (smooth interpolation).

**Equal chemical potentials at each point**:

$$ \mu(c_\alpha) = \mu(c_\beta) $$

This decouples chemistry from gradient → standard interface energy.

### 20.6 Numerical methods

**Explicit Euler** (simple but stability):
- $\Delta t < c \cdot \Delta x^2$ for diffusion-like
- $\Delta t < c \cdot \Delta x^4$ for Cahn-Hilliard
- Very restrictive

**Implicit / Semi-implicit**:
- Linear: Lin's scheme
- Spectral: FFT-based (periodic) — fast
- ADI: Alternating Direction Implicit

**Adaptive mesh refinement (AMR)**:
- Fine mesh at interface
- Coarse elsewhere
- MOOSE supports this natively

### 20.7 习题

**20.1**: Implement explicit Euler 1D Allen-Cahn.

**20.2**: Derive KKS equilibrium condition $\mu(c_\alpha) = \mu(c_\beta)$.

**20.3**: Compute time step constraint for Cahn-Hilliard.

**20.4**: Why is anti-trapping flux needed?

**20.5**: Code FFT-spectral Cahn-Hilliard.

## 第 21 章 相场应用

### 21.1 Solidification

**Setup**:
- 多场: phase $\phi$ + concentration $c$
- Free energy: $f(c, T) - W \phi^2(1-\phi)^2$
- Initially: liquid + small solid nucleus
- 边界: thermal gradient (directional)

**Outputs**:
- Dendritic morphology
- Primary dendrite arm spacing
- Microsegregation profiles
- Cooling-rate effects

**Key paper**: Karma 2001 quantitative phase-field for solidification.

### 21.2 Grain growth — multi-orientation

**Order parameters**: $\eta_i$, i = 1...N (grain orientations).

**Free energy**:

$$ F = \int \left[\sum_i f_{DW}(\eta_i) + \gamma \sum_{i \neq j} \eta_i^2 \eta_j^2 + \frac{\kappa}{2}\sum_i (\nabla \eta_i)^2\right] dV $$

- $\gamma \eta_i^2 \eta_j^2$: 抑制 grains overlap

**Outputs**:
- Average grain size vs time: $\bar{R} \sim \sqrt{Mt}$
- Grain size distribution
- Texture evolution

### 21.3 Precipitation in superalloys

**Ni-base superalloy γ + γ' (L1_2)**:

**Phase-field setup**:
- $\phi$ = phase indicator (γ vs γ')
- $c_i$ = composition fields (multiple elements)
- Coupled with CALPHAD G
- Elastic with γ/γ' misfit

**Results** (PRISMS-PF examples):
- Cuboidal γ' shapes (elastic favorable)
- Coalescence + coarsening
- Particle size distribution
- LSW behavior at long times

### 21.4 Martensite transformation

**Multi-variant martensite**:
- 24 variants for cubic→tetragonal
- $\phi_i$ for each variant
- Strain-driven (not chemistry)

**Free energy dominated by**: elastic strain energy + interface energy.

**Outputs**:
- Microstructure (lamellar martensite)
- Self-accommodation
- Transformation strain

### 21.5 Ferroelectric domains

**Order parameter**: polarization vector $P_i$.

**Landau free energy**:

$$ f = \alpha P^2 + \beta P^4 + \gamma P^6 $$

with $\alpha$ depending on T.

**Coupled with**: elastic + electric field.

**Output**: domain patterns, switching dynamics.

### 21.6 Phase-field fracture

**Bourdin-Francfort-Marigo formulation**:

$$ F = \int_V \left[(1-d)^2 \psi^+(\epsilon) + \frac{G_c}{2}\left(\frac{d^2}{l_c} + l_c |\nabla d|^2\right)\right] dV $$

- $d \in [0, 1]$: damage (0 intact, 1 cracked)
- $\psi^+$: tensile elastic energy
- $G_c$: fracture energy
- $l_c$: regularization length

**Outputs**: 
- Crack initiation
- Propagation paths
- Branching

### 21.7 Electrochemistry — battery interfaces

**Phase-field for Li-ion intercalation**:
- $\phi$: phase (Li-poor vs Li-rich)
- $c$: Li concentration
- Coupled with electrochemical potential

**Outputs**:
- Phase separation in LFP
- Solid electrolyte interphase (SEI)
- Dendrite growth (Li plating)

### 21.8 Recent advances (2023-2024)

- **CALPHAD-coupled multi-component PF** (mature)
- **Phase-field + machine learning** (surrogate)
- **Adaptive AMR with PRISMS-PF**
- **Multi-physics PF** (electrochemical + mechanical + thermal)
- **GPU-accelerated PF** (CUDA)

### 21.9 习题

**21.1**: Set up grain growth simulation, observe $R \sim \sqrt{t}$.

**21.2**: Solidification with anti-trapping flux, check 微分离 quantitative.

**21.3**: Precipitation: compute γ' size distribution + LSW exponent.

**21.4**: Phase-field fracture: simulate notched tension specimen.

**21.5**: Li-ion battery: phase separation in LiFePO₄.

## 第 22 章 相场实战

### 22.1 FiPy detailed tutorial

**FiPy = Python + finite volume PDE**

**Install**:

```bash
pip install fipy
```

**1D Cahn-Hilliard complete**:

```python
from fipy import (
    Grid1D, CellVariable, TransientTerm, DiffusionTerm,
    ImplicitDiffusionTerm, ExponentialNoiseVariable
)
import numpy as np
import matplotlib.pyplot as plt

# Domain
nx = 200
dx = 0.5
mesh = Grid1D(dx=dx, nx=nx)

# Variable
phi = CellVariable(name="phi", mesh=mesh)

# Initial: small random perturbation around 0.5
phi.setValue(0.5 + 0.01 * np.random.randn(nx))

# Parameters
W = 1.0    # well depth
kappa = 1.0  # gradient coefficient
M = 1.0   # mobility

# f' = 4 W phi (phi - 0.5) (phi - 1) but here we use phi(1-phi)(1-2phi) form
# df/dphi for f = W phi^2(1-phi)^2 = 2 W phi (1-phi)(1-2phi)
# Variational: mu = df/dphi - kappa nabla^2 phi

# Cahn-Hilliard system:
# d phi / d t = nabla . M nabla mu
# mu = df/dphi - kappa nabla^2 phi

# 2-equation system in FiPy
mu = CellVariable(name="mu", mesh=mesh)

# Equation 1: time evolution
eq1 = TransientTerm(var=phi) == DiffusionTerm(coeff=M, var=mu)

# Equation 2: chemical potential (steady-state in each step)
df_dphi = 2 * W * phi * (1 - phi) * (1 - 2 * phi)
eq2 = ImplicitDiffusionTerm(coeff=kappa, var=phi) + df_dphi == mu

# Coupled
eq = eq1 & eq2

# Time stepping
dt = 0.1
n_steps = 5000

# Output
snapshots = []
for step in range(n_steps):
    eq.solve(dt=dt)
    if step % 500 == 0:
        snapshots.append(phi.value.copy())
        print(f"Step {step}: phi range [{phi.value.min():.3f}, {phi.value.max():.3f}]")

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
x = mesh.cellCenters[0]
for i, snap in enumerate(snapshots):
    ax.plot(x, snap, label=f"t={i*500*dt}", alpha=0.6)
ax.set_xlabel("x"); ax.set_ylabel("phi"); ax.legend(loc='upper right', fontsize=8)
plt.title("1D Cahn-Hilliard spinodal decomposition")
plt.savefig("cahn_hilliard_1d.png", dpi=200)
```

**2D extension**:

```python
from fipy import Grid2D

nx = ny = 100
dx = dy = 0.5
mesh = Grid2D(dx=dx, dy=dy, nx=nx, ny=ny)
# ... rest similar
```

### 22.2 MOOSE-PF tutorial

**MOOSE = Multi-physics Object-Oriented Simulation Environment**

**Install**: Follow https://mooseframework.inl.gov/getting_started/installation/ (1-2 hours).

**Input file structure**:

```yaml
[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 100
  ny = 100
  xmin = 0
  xmax = 100
  ymin = 0
  ymax = 100
[]

[Variables]
  [phi]
    initial_condition = 0
  []
[]

[ICs]
  [random_init]
    type = RandomIC
    variable = phi
    min = 0
    max = 1
  []
[]

[Kernels]
  [time]
    type = TimeDerivative
    variable = phi
  []
  [diffusion]
    type = MatDiffusion
    variable = phi
    diffusivity = M
  []
  [bulk]
    type = AllenCahn
    variable = phi
    mob_name = M
    f_name = F
  []
[]

[Materials]
  [free_energy]
    type = DerivativeParsedMaterial
    f_name = F
    args = phi
    function = '4 * phi^2 * (1 - phi)^2'  # W = 4 for example
    derivative_order = 2
  []
  [mobility]
    type = ConstantMaterial
    prop_names = M
    prop_values = 1.0
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  dt = 0.1
  num_steps = 1000
  solve_type = 'PJFNK'
[]

[Outputs]
  exodus = true
  interval = 50
[]
```

**Run**:

```bash
moose-opt -i input.i
```

**Visualize**: Paraview opens .exodus file.

### 22.3 PRISMS-PF tutorial

**PRISMS = Modern phase-field framework** (U. Michigan).

**Repository**: https://github.com/prisms-center/phaseField

**Built-in applications**:
- Solidification (dendrite)
- Grain growth
- Cahn-Hilliard (spinodal)
- Precipitation
- KKS model
- Phase-field fracture

**Setup typical**:

```cpp
// equation.h
template <int dim, int degree>
void
customPDE<dim, degree>::residualLHS(
    [const list of cell-data])
{
    // Define equations
    EquationLHS(0, "phi") = ...;
}
```

**Run on HPC**:

```bash
mpirun -np 64 ./main
```

### 22.4 OpenPhase

**OpenPhase**: C++ phase-field for materials.

**Strong in**:
- Multi-phase materials
- Industrial applications
- Coupling with thermodynamic databases

**License**: GPL.

### 22.5 MICRESS (commercial)

**MICRESS**: Industry standard for phase-field solidification + precipitation.

**Strengths**:
- Mature
- 3D multi-component
- CALPHAD coupling (Thermo-Calc)
- Industrial robustness

**License**: Commercial.

### 22.6 Post-processing详细

**Phase fraction over time**:

```python
import numpy as np
import meshio

# Load output
mesh = meshio.read("output.exodus")

# Time series
for t_idx in range(mesh.point_data['phi'].shape[1]):
    phi_t = mesh.point_data['phi'][:, t_idx]
    f_phase1 = np.mean(phi_t)
    # ...
```

**Grain size from segmentation**:

```python
from skimage.measure import label, regionprops
from skimage.segmentation import watershed
import numpy as np

# Threshold
binary = phi_field > 0.5

# Watershed segmentation
distance = ndi.distance_transform_edt(binary)
local_max = peak_local_max(distance, min_distance=5)
markers = ndi.label(local_max)[0]
labels = watershed(-distance, markers, mask=binary)

# Region properties
regions = regionprops(labels)
sizes = [r.equivalent_diameter * dx for r in regions]
print(f"Mean: {np.mean(sizes):.2f}, Std: {np.std(sizes):.2f}")
```

**Interface curvature**:

```python
# From phi field, compute curvature
phi_x, phi_y = np.gradient(phi, dx)
phi_xx = np.gradient(phi_x, dx, axis=0)
phi_yy = np.gradient(phi_y, dx, axis=1)
phi_xy = np.gradient(phi_x, dx, axis=1)

mag_grad = np.sqrt(phi_x**2 + phi_y**2)
curvature = (phi_xx*phi_y**2 - 2*phi_xy*phi_x*phi_y + phi_yy*phi_x**2) / (mag_grad**3 + 1e-10)
```

### 22.7 习题（多个 case studies）

**22.1**: FiPy 完整 1D Cahn-Hilliard, vary W and observe spinodal pattern.

**22.2**: MOOSE 2D grain growth, compute mean grain size vs time, check $\bar{R} \sim \sqrt{t}$.

**22.3**: PRISMS-PF dendrite solidification, vary thermal gradient.

**22.4**: Precipitation simulation: γ' in Ni-base, vary aging temperature.

**22.5**: Phase-field fracture: simulate L-shaped specimen, predict crack path.

## 第 23 章 CALPHAD-coupled Phase-field

### 23.1 Why coupling matters

**Without CALPHAD**: f(c) assumed (e.g., parabolic).
**With CALPHAD**: f(c, T) from real thermodynamic database.

→ **Quantitative multi-component phase-field**.

### 23.2 TC-Python integration

```python
from tc_python import *

with TCPython() as session:
    sys = session.set_cache_folder("cache") \
        .select_database_and_elements("TCNI11", ["Ni","Al","Cr"]) \
        .get_system()
    
    # Build G surface for use in phase-field
    # Grid in (T, c_Al, c_Cr)
    T_range = np.linspace(800, 1300, 20) + 273
    c_Al_range = np.linspace(0.0, 0.25, 25)
    c_Cr_range = np.linspace(0.0, 0.25, 25)
    
    G_table_gamma = np.zeros((20, 25, 25))
    G_table_gamma_prime = np.zeros((20, 25, 25))
    
    for i, T in enumerate(T_range):
        for j, c_Al in enumerate(c_Al_range):
            for k, c_Cr in enumerate(c_Cr_range):
                c_Ni = 1 - c_Al - c_Cr
                if c_Ni < 0:
                    continue
                
                # FCC_A1 (γ)
                calc_g = sys.with_single_equilibrium_calculation() \
                    .set_condition("T", T) \
                    .set_condition("W(NI)", c_Ni) \
                    .set_condition("W(AL)", c_Al) \
                    .set_condition("W(CR)", c_Cr) \
                    .set_phase_to_fixed("FCC_A1", 1.0)
                # ... get G
                
                G_table_gamma[i,j,k] = ...
                
                # L12 (γ')
                # Similarly
                G_table_gamma_prime[i,j,k] = ...

# Save table
np.savez("G_tables.npz", 
         T=T_range, c_Al=c_Al_range, c_Cr=c_Cr_range,
         G_gamma=G_table_gamma, G_gamma_prime=G_table_gamma_prime)
```

### 23.3 PyCalphad-based surrogate

```python
from scipy.interpolate import RegularGridInterpolator
import numpy as np

# Load
data = np.load("G_tables.npz")

G_gamma_interp = RegularGridInterpolator(
    (data['T'], data['c_Al'], data['c_Cr']),
    data['G_gamma'],
    bounds_error=False, fill_value=None
)

# Use in phase-field
def f_bulk(phi, c_Al, c_Cr, T):
    # h(phi): interpolation function 0 -> 1
    h = phi**3 * (10 - 15*phi + 6*phi**2)
    
    G_gamma_val = G_gamma_interp((T, c_Al, c_Cr))
    G_gp_val = G_gamma_prime_interp((T, c_Al, c_Cr))
    
    # Mix + double-well
    f_chem = (1 - h) * G_gamma_val + h * G_gp_val
    f_dw = W * phi**2 * (1 - phi)**2
    
    return f_chem + f_dw
```

### 23.4 Real example — γ' precipitation

**Setup**:
- Phase-field for γ → γ + γ'
- 5 elements: Ni, Al, Cr, Co, Ti
- CALPHAD-coupled
- Elastic with γ/γ' misfit

**Output**: realistic γ' microstructure matching experiment.

### 23.5 加速 calls

CALPHAD is expensive per call. Speed up:

**Method 1**: Pre-tabulate G(T, x) → interpolate.
**Method 2**: Neural network surrogate (NN learns G).
**Method 3**: Sparse grids for high-D.

### 23.6 习题

**23.1**: Build G(T, x) table for binary Fe-C using PyCalphad.

**23.2**: Use as input in 1D Allen-Cahn for austenite→ferrite.

**23.3**: 3D phase-field of γ' precipitation with PyCalphad surrogate.

**23.4**: Compare CALPHAD-coupled vs simplified parabolic free energy.

**23.5**: Train NN to replace PyCalphad calls → 100× speedup.

---

# 第 18 章后扩展 — CALPHAD UQ + Industrial cases

(放在原 Ch 17 后作为深化)

## 17.A CALPHAD 工业应用案例

### Case 1: 高强度钢

**Goal**: Design DP980 dual-phase steel (50% ferrite + 50% martensite, 980 MPa UTS).

**Workflow**:
1. CALPHAD predict austenite stability vs (C, Mn, Si)
2. Find composition giving ~50% austenite at intercritical T
3. Quench to form martensite
4. CALPHAD predict tempered cementite distribution

### Case 2: Single crystal Ni superalloy

**Goal**: Optimize γ' size for creep resistance at 1050°C.

**Workflow**:
1. CALPHAD γ' solvus
2. DICTRA γ' coarsening kinetics
3. Aging schedule optimization

### Case 3: Lithium battery cathode

**Goal**: Phase stability of Li_x Ni_y Co_z Mn_w O₂ during charge/discharge.

**Workflow**:
1. FactSage / PyCalphad with oxide thermo
2. Predict phase transitions at high x_Li
3. Identify safe SOC operating window

### Case 4: Welding (HAZ)

**Goal**: Predict heat-affected zone microstructure in high-strength steel welding.

**Workflow**:
1. Rosenthal thermal field
2. CALPHAD local equilibrium
3. DICTRA solute redistribution
4. Final phase + properties

### 17.B Multi-fidelity CALPHAD

**Combine**:
- DFT (cheap when run, accurate but 0K)
- Experimental (1-2 datapoints per system, expensive)
- ML predictions (cheap, intermediate)

**Bayesian framework** integrates all → best estimate + UQ.

---

