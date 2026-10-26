"""Verify displayed numerical table values against the single model output."""
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]

def read_table(number):
    with (ROOT / 'tables' / f'Table_{number}.csv').open(encoding='utf-8', newline='') as f:
        return list(csv.reader(f))[1:]

def rounded_equal(text, value):
    normalized = text.replace('−', '-').replace('%', '').replace(',', '').strip()
    digits = len(normalized.split('.')[1]) if '.' in normalized else 0
    if abs(float(normalized) - value) > .50001 * 10 ** -digits:
        raise AssertionError(f'Displayed {text} does not match computed {value}')

def verify():
    r = json.loads((ROOT / 'outputs/model_results.json').read_text(encoding='utf-8'))
    f = json.loads((ROOT / 'data/derived/nri_aggregation_results.json').read_text(encoding='utf-8'))
    b = r['base']; scenarios = {z['label']: z for z in r['scenarios']}
    for row, geo in zip(read_table(1), ['United States', 'California']):
        rounded_equal(row[1], f['annual_building_value_eal'][geo] / 1e9)
    inputs = {row[0]: row[1] for row in read_table(2)}
    for label, val in [('Projects N', b['N']), ('Technical correlation ρ', b['rho']), ('Real discount rate d', 100*b['d']), ('Commissioning year T', b['lag']), ('Covered loss share a', 100*b['a']), ('Annual maintenance ratio m', 100*b['m']), ('Effectiveness r', 100*b['r'])]:
        rounded_equal(inputs[label], val)
    adoption = next(z['rows'] for z in r['adoptionCurves'] if z['K0'] == .6)
    for row in read_table(3):
        a = float(row[0].replace('%', '')) / 100
        z = min(adoption, key=lambda x: abs(x['a']-a))
        if abs(z['a']-a) > 1e-10:
            raise AssertionError('Adoption output missing')
        for text, value in zip(row[1:], [z['D']/1e6, 100*z['rmin'], 100*z['theta']]):
            rounded_equal(text, value)
    for row, z in zip(read_table(4), r['comparators']):
        for text, value in zip(row, [z['b'], 100*z['rmin'], z['advantage']/1e6, z['optimum']['N']]):
            rounded_equal(text, value)
    for row, z in zip(read_table(5), r['costComparison']):
        for text, value in zip(row[:3], [z['K0'], 100*z['floor'], 100*z['rmin']]):
            rounded_equal(text, value)
        if (row[3] == 'Infeasible') != (not z['feasibleAtFullEffectiveness']):
            raise AssertionError('Feasibility wording disagrees with model')
    pairs = [
        ('Discount 2%', 'Discount 7%'), ('Base 3%', 'Commissioning year 15'),
        ('Initial cost ratio 0.3', 'Initial cost ratio 1.2'), ('Maintenance 0%', 'Maintenance 2%'),
        ('Adoption 1%', 'Adoption 10%'), ('Success 2.5%', 'Success 10%'),
        ('Base 3%', 'Correlation 0.5'), ('Loss half fixed deployment cash', 'Loss 1.5 times fixed deployment cash'),
        ('Base 3%', 'Maturation'),
    ]
    for row, pair in zip(read_table(6), pairs):
        for text, label in zip(row[2].split(' to '), pair):
            rounded_equal(text, 100*scenarios[label]['rmin'])
    v = r['voi']
    states = [
        (v['pos']*v['qpos'], v['benefit_useful']-v['deployment_cost']),
        (v['neg']*v['qneg'], 0),
        (v['pos']*(1-v['qpos']), -v['deployment_cost']),
        (v['neg']*(1-v['qneg']), 0),
    ]
    for row, (probability, payoff) in zip(read_table(7), states):
        rounded_equal(row[2], probability)
        rounded_equal(row[4], payoff)
    return {'tables_checked': 7, 'rounded_numeric_values': 'passed'}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
