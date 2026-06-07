"""
m01_basics.py — 第〇/一篇 · 入门与全景

Computational materials science scaffolding:
  - Unit conversions (eV, Hartree, Joule, K, fs, ...)
  - Common physical constants
  - File-format awareness (POSCAR / xyz / cif sniffing)
  - Workflow timing decorator
"""

import math
import time
from functools import wraps

# ---------- Physical constants (SI + chemistry-friendly) ----------
KB_EV     = 8.617333262e-5      # Boltzmann (eV/K)
KB_J      = 1.380649e-23        # Boltzmann (J/K)
HBAR_JS   = 1.054571817e-34     # ℏ (J·s)
E_CHARGE  = 1.602176634e-19     # elementary charge (C)
N_A       = 6.02214076e23       # Avogadro
EV2J      = 1.602176634e-19
J2EV      = 6.241509e18
HARTREE2EV = 27.211386245988
BOHR2A    = 0.529177210903

# ---------- Unit conversions ----------
def k_to_kt_ev(T_K: float) -> float:
    """k_B T in eV at temperature T (Kelvin). Sanity at 300 K ≈ 0.025852 eV."""
    return KB_EV * T_K

def energy_per_atom(E_total_eV: float, n_atoms: int) -> float:
    return E_total_eV / n_atoms

def formation_energy(E_compound: float, E_pure: dict, n_pure: dict,
                     n_compound: int) -> float:
    """E_f per atom = (E_AB - n_A E_A - n_B E_B) / n_total
    E_pure: {'A': E_per_atom_A_eV, 'B': ...}
    n_pure: {'A': count_in_compound, 'B': ...}"""
    refs = sum(n_pure[k] * E_pure[k] for k in n_pure)
    return (E_compound - refs) / n_compound

# ---------- Workflow timing ----------
def timed(label=None):
    def deco(fn):
        @wraps(fn)
        def wrap(*a, **kw):
            t0 = time.perf_counter()
            r = fn(*a, **kw)
            dt = time.perf_counter() - t0
            print(f"  [{label or fn.__name__}] {dt*1000:.1f} ms")
            return r
        return wrap
    return deco

# ---------- File-format sniff ----------
def detect_format(path: str) -> str:
    """Quick MIME-like sniff for common materials files."""
    suffix = path.lower().split('.')[-1]
    if suffix == 'cif':                  return 'crystallographic-cif'
    if suffix in ('xyz',):               return 'atomic-xyz'
    if suffix in ('poscar',):            return 'vasp-poscar'
    if 'poscar' in path.lower():         return 'vasp-poscar'
    if suffix == 'lammps':               return 'lammps-data'
    if suffix in ('h5','hdf5','nc'):     return 'hdf5/netcdf-binary'
    if suffix == 'tdb':                  return 'thermo-calc-tdb'
    if suffix == 'csv':                  return 'tabular-csv'
    if suffix == 'json':                 return 'json'
    return 'unknown'

# ---------- Demo ----------
@timed("compute kT at 1000 K")
def demo():
    print(f"kT at 300 K  = {k_to_kt_ev(300):.4f} eV")
    print(f"kT at 1000 K = {k_to_kt_ev(1000):.4f} eV")
    print(f"kT at 1500 K = {k_to_kt_ev(1500):.4f} eV")

    # Mock formation energy: Cu3Au (one fcc unit cell, 4 atoms = 3 Cu + 1 Au)
    E_Cu = -3.71     # eV/atom (PBE bulk Cu)
    E_Au = -3.05     # eV/atom (PBE bulk Au)
    E_Cu3Au = 4 * (-3.60)  # total energy of Cu3Au, eV
    e_f = formation_energy(E_Cu3Au, {'Cu': E_Cu, 'Au': E_Au},
                                    {'Cu': 3, 'Au': 1}, 4)
    print(f"Cu3Au formation energy = {e_f*1000:.0f} meV/atom (expected ≈ -60 meV/atom)")

    for f in ['POSCAR', 'graphene.xyz', 'gpu_run.h5', 'CrFeNi.tdb', 'data.csv']:
        print(f"  detect_format({f!r}) -> {detect_format(f)}")

if __name__ == '__main__':
    demo()
