"""Create machine-readable numerical outputs from the single JS model run."""
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]

def write_csv(name, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT / 'outputs' / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)

def export():
    r = json.loads((ROOT / 'outputs/model_results.json').read_text(encoding='utf-8'))
    write_csv('base_case.csv', [r['base']])
    write_csv('sensitivity_scenarios.csv', r['scenarios'])
    write_csv('opportunity_cost_comparison.csv', r['comparators'])
    write_csv('commissioning_cost_comparison.csv', r['costComparison'])
    write_csv('commissioning_cost_limits.csv', [{k: v for k, v in r['costTargets'].items() if k != 'commissioning_max_curve'}])
    write_csv('commissioning_cost_limit_curve.csv', r['costTargets']['commissioning_max_curve'])
    write_csv('conditional_research_ceiling.csv', [r['researchCeilings']])
    write_csv('portfolio_curves.csv', [row for s in r['portfolios'] for row in s['rows']])
    write_csv('commissioning_cost_curves.csv', [row for s in r['costCurves'] for row in s['rows']])
    write_csv('adoption_curves.csv', [row for s in r['adoptionCurves'] for row in s['rows']])
    write_csv('cash_cost_distribution.csv', r['cash']['rows'])
    write_csv('convex_adoption.csv', [r['convex']])
    write_csv('value_of_information.csv', [r['voi']])
    return r

if __name__ == '__main__':
    export()
    print('Exported model CSV files')
