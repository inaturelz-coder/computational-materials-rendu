"""
m12_software_path.py — 收尾：软件生态 + 5 年成长路径

Demos:
  - Environment sanity check (numpy / scipy / sklearn / ase / pymatgen / pycalphad / mace…)
  - Print the canonical 5-year learning roadmap
"""

import importlib
import sys

PACKAGES_BY_TIER = {
    'core (everyone)': [
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('matplotlib', 'Matplotlib'),
        ('pandas', 'pandas'),
    ],
    'ML (year 2+)': [
        ('sklearn', 'scikit-learn'),
        ('torch', 'PyTorch'),
        ('jax', 'JAX (optional)'),
    ],
    'materials core (year 1+)': [
        ('ase', 'ASE — Atomic Simulation Environment'),
        ('pymatgen', 'pymatgen'),
        ('matminer', 'matminer (features)'),
    ],
    'thermo / kinetics (year 2+)': [
        ('pycalphad', 'pycalphad'),
        ('espei', 'ESPEI'),
    ],
    'MLIP (year 2-3)': [
        ('mace', 'MACE'),
        ('m3gnet', 'M3GNet'),
        ('chgnet', 'CHGNet'),
    ],
    'phase-field / FEM (year 3+)': [
        ('fenics', 'FEniCS (optional)'),
        ('moose', 'MOOSE (HPC)'),
    ],
}

def check_environment():
    """Print which packages are installed and which are missing."""
    print("=== Computational Materials environment check ===\n")
    for tier, pkgs in PACKAGES_BY_TIER.items():
        print(f"--- {tier} ---")
        for mod_name, display in pkgs:
            try:
                m = importlib.import_module(mod_name)
                ver = getattr(m, '__version__', '?')
                print(f"  ✓ {display:<32}  v{ver}")
            except ImportError:
                print(f"  ✗ {display:<32}  (not installed)")
        print()

ROADMAP_5_YEAR = """
─────────────────────────────────────────────────
  5-Year Path to Computational Materials Expert
─────────────────────────────────────────────────

Year 1 — Foundation
  • Math: linear algebra, calculus, statistics (m07–m09)
  • Python + numpy + scipy + git
  • Crystallography + thermodynamics basics
  • Try DFT (VASP/QE) on a simple bulk system (m02)
  • Learn ASE + pymatgen workflows

Year 2 — Atomistic Mastery
  • DFT convergence + post-processing (DOS, band, EOS)
  • MD with LAMMPS + EAM/MEAM (m03)
  • First MLIP run: MACE-MP-0 zero-shot
  • CALPHAD basics with pycalphad (m04)

Year 3 — Mesoscale + Data
  • Phase-field (Cahn-Hilliard, Allen-Cahn) (m05)
  • Coupling CALPHAD ↔ PF
  • Bayesian Optimization for alloy design (m08)
  • GPs and active learning (m07)
  • UQ basics (m09)

Year 4 — Integration (ICME)
  • Build your first 3-stage pipeline (DFT → CALPHAD → PF)
  • Train your own MLIP for your specific alloy
  • Snakemake / FireWorks reproducible workflows
  • Publish first methodology paper

Year 5 — Domain Mastery + Original Contribution
  • Lead a multi-scale ICME case study (m11)
  • Open-source a tool / database for the community
  • Mentor junior researchers
  • Define your research program for the next 5 years
─────────────────────────────────────────────────
"""

# ---------- Demo ----------
def demo():
    check_environment()
    print(ROADMAP_5_YEAR)

if __name__ == '__main__':
    demo()
