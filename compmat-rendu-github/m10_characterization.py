"""
m03_md_mlip.py — 任脉第 2 步：MD + MLIP (原子尺度)

Demos:
  - Lennard-Jones MD: velocity-Verlet, NVE, energy conservation check
  - Radial distribution function g(r)
  - MLIP interface stub: how to wrap MACE/M3GNet-style ASE calculators
"""

import numpy as np
import math

# ---------- Lennard-Jones potential ----------
def lj_forces_energy(positions, box_L, eps=1.0, sigma=1.0, rc=2.5):
    """Compute LJ forces and total energy in PBC box."""
    N = len(positions)
    forces = np.zeros_like(positions)
    energy = 0.0
    rc2 = rc * rc
    for i in range(N - 1):
        ri = positions[i]
        for j in range(i + 1, N):
            rij = positions[j] - ri
            rij -= box_L * np.round(rij / box_L)
            r2 = float(rij @ rij)
            if r2 > rc2 or r2 < 1e-12:
                continue
            inv2 = sigma * sigma / r2
            inv6 = inv2 ** 3
            inv12 = inv6 ** 2
            energy += 4 * eps * (inv12 - inv6)
            fmag = 24 * eps * (2 * inv12 - inv6) / r2
            forces[i] -= fmag * rij
            forces[j] += fmag * rij
    return forces, energy

# ---------- Velocity-Verlet NVE integrator ----------
def md_run(N=64, density=0.85, T_init=1.0, n_steps=200, dt=0.005, rc=2.5):
    """Simple LJ MD in reduced units; returns (energies, temperatures)."""
    box_L = (N / density) ** (1.0 / 3.0)
    # Initialize on lattice
    n_side = int(math.ceil(N ** (1.0 / 3.0)))
    a = box_L / n_side
    positions = np.array([[i, j, k] for i in range(n_side)
                                    for j in range(n_side)
                                    for k in range(n_side)],
                          dtype=float)[:N] * a
    rng = np.random.default_rng(42)
    velocities = rng.normal(0, math.sqrt(T_init), (N, 3))
    velocities -= velocities.mean(axis=0)            # remove drift
    velocities *= math.sqrt(T_init / ((velocities**2).sum() / (3 * N)))

    forces, U = lj_forces_energy(positions, box_L, rc=rc)
    Es, Ts = [], []
    for step in range(n_steps):
        velocities += 0.5 * dt * forces
        positions += dt * velocities
        positions %= box_L                            # PBC wrap
        forces, U = lj_forces_energy(positions, box_L, rc=rc)
        velocities += 0.5 * dt * forces
        KE = 0.5 * (velocities ** 2).sum()
        T = (2.0 / 3.0) * KE / N
        Es.append(U + KE); Ts.append(T)
    return np.array(Es), np.array(Ts)

# ---------- Radial distribution function g(r) ----------
def rdf(positions, box_L, n_bins=50, r_max=None):
    """Pair RDF for a snapshot (PBC)."""
    N = len(positions)
    if r_max is None:
        r_max = box_L / 2
    bins = np.linspace(0, r_max, n_bins + 1)
    hist = np.zeros(n_bins)
    for i in range(N - 1):
        for j in range(i + 1, N):
            rij = positions[j] - positions[i]
            rij -= box_L * np.round(rij / box_L)
            r = np.linalg.norm(rij)
            if r < r_max:
                k = int(r / r_max * n_bins)
                if k < n_bins:
                    hist[k] += 2
    rho = N / box_L ** 3
    r_mid = 0.5 * (bins[1:] + bins[:-1])
    shell_V = 4 / 3 * math.pi * (bins[1:] ** 3 - bins[:-1] ** 3)
    g = hist / (rho * N * shell_V)
    return r_mid, g

# ---------- MLIP wrapper stub ----------
def mlip_predict(positions, species, model_name='MACE-MP-0'):
    """Stub for MLIP energy/force prediction.
    In production:
        from mace.calculators import mace_mp
        calc = mace_mp(model='medium')
        atoms.calc = calc
        E = atoms.get_potential_energy()
        F = atoms.get_forces()
    """
    return {
        'model': model_name,
        'note': 'wrap via ASE Calculator; not run here',
        'mock_energy_per_atom_eV': -3.5 + 0.01 * np.random.randn(),
    }

# ---------- Demo ----------
def demo():
    print("=== LJ NVE molecular dynamics demo ===\n")
    Es, Ts = md_run(N=27, T_init=1.0, n_steps=80, dt=0.004)
    print(f"E_total drift (first vs last 20 avg): "
          f"{abs(Es[:20].mean() - Es[-20:].mean()) / abs(Es.mean()) * 100:.2f}% "
          f"(should be < a few %)")
    print(f"T_init = 1.0  →  T_final = {Ts[-20:].mean():.2f}\n")
    print(f"MLIP stub: {mlip_predict(None, ['Cu']*10)}")

if __name__ == '__main__':
    demo()
