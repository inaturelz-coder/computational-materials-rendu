"""
test_all_modules.py — Run all 12 demos and assert they execute without error.
"""

import importlib
import sys
import traceback

MODULES = [
    ('m01_basics',          '入门与全景 / Basics'),
    ('m02_dft',             'DFT  (任脉 1)'),
    ('m03_md_mlip',         'MD + MLIP  (任脉 2)'),
    ('m04_calphad',         'CALPHAD  (任脉 3)'),
    ('m05_phasefield',      'Phase-field  (任脉 4)'),
    ('m06_cpfem',           'CP-FEM  (任脉 5)'),
    ('m07_ml',              'ML for materials  (督脉 2)'),
    ('m08_bo',              'BO + MCMC  (督脉 3)'),
    ('m09_uq',              'UQ  (督脉 4)'),
    ('m10_characterization','表征 / Characterization  (督脉 1)'),
    ('m11_icme',            'ICME closed loop  (交汇)'),
    ('m12_software_path',   '软件生态 + 5 年路径  (收尾)'),
]

def main():
    passed = 0
    failed = []
    for mod_name, label in MODULES:
        print(f"\n{'=' * 60}\nTesting {mod_name} — {label}\n{'=' * 60}")
        try:
            m = importlib.import_module(mod_name)
            if hasattr(m, 'demo'):
                m.demo()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
            failed.append((mod_name, str(e)))

    print(f"\n{'=' * 60}")
    print(f"  Passed: {passed} / {len(MODULES)}")
    if failed:
        print(f"  Failed:")
        for mod, err in failed:
            print(f"    - {mod}: {err}")
    print(f"{'=' * 60}")
    return 0 if not failed else 1

if __name__ == '__main__':
    sys.exit(main())
