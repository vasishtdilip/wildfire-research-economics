"""Reproduce the archived loss baseline, model outputs and figures offline."""
from pathlib import Path
import argparse, importlib.util, json, os, platform, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True

def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-figures', action='store_true', help='Run numerical checks without matplotlib')
    parser.add_argument('--node', default=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE') or shutil.which('node'), help='Path to a Node.js executable')
    args = parser.parse_args()
    if not args.node:
        parser.error('Node.js is required; install Node.js or pass --node PATH')
    (ROOT / 'outputs').mkdir(exist_ok=True)
    fema = load_module('aggregate_fema', 'code/aggregate_fema.py').aggregate()
    proc = subprocess.run([args.node, str(ROOT / 'code/wildfire_economics_model.js')], check=True, capture_output=True, text=True)
    model = json.loads(proc.stdout)
    if abs(model['base']['L'] - fema['annual_building_value_eal']['United States']) > .0001:
        raise AssertionError('Model national baseline differs from archived FEMA aggregation')
    california = next(z for z in model['scenarios'] if z['label'] == 'California')
    if abs(california['L'] - fema['annual_building_value_eal']['California']) > .0001:
        raise AssertionError('Model California baseline differs from archived FEMA aggregation')
    (ROOT / 'outputs/model_results.json').write_text(json.dumps(model, indent=2) + '\n', encoding='utf-8')
    load_module('export_results', 'code/export_results.py').export()
    table_checks = load_module('verify_tables', 'code/verify_tables.py').verify()
    versions = {'python': platform.python_version(), 'node': subprocess.check_output([args.node, '--version'], text=True).strip()}
    if not args.skip_figures:
        import matplotlib
        versions['matplotlib'] = matplotlib.__version__
        subprocess.run([sys.executable, str(ROOT / 'code/plot_figures.py')], check=True)
    report = {
        'status': 'passed', 'runtime_versions': versions,
        'raw_records': fema['raw_counties_and_equivalents'], 'retained_counties': fema['counties'],
        'US_building_EAL': model['base']['L'], 'California_building_EAL': california['L'],
        'base_rmin': model['base']['rmin'], 'base_NPV': model['base']['W'],
        'commissioning_cost_limit': model['costTargets']['commissioning_max_break_even'],
        'b2_commissioning_cost_limit': model['costTargets']['commissioning_max_b2'],
        'conditional_research_PV_ceiling': model['researchCeilings']['expected_research_pv_ceiling'],
        'numerical_assertions': 'passed', 'table_checks': table_checks, 'figures_regenerated': not args.skip_figures,
    }
    (ROOT / 'outputs/verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
