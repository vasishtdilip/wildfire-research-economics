"""Aggregate archived FEMA county building-value expected annual loss, offline."""
from pathlib import Path
import csv, json, math

ROOT = Path(__file__).resolve().parents[1]
STATES = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split())
FIELDS = ['STATE', 'STATEABBRV', 'COUNTY', 'STCOFIPS', 'WFIR_EALB', 'NRI_VER']

def aggregate():
    raw = ROOT / 'data/raw'
    rows = []
    for name in ['nri_counties_0.json', 'nri_counties_2000.json']:
        obj = json.loads((raw / name).read_text(encoding='utf-8'))
        if 'error' in obj:
            raise ValueError(f'Archived source error in {name}')
        rows.extend(f['attributes'] for f in obj['features'])
    if len(rows) != 3232 or len({r['STCOFIPS'] for r in rows}) != 3232:
        raise AssertionError('Expected 3,232 unique county/equivalent records')
    combined = json.loads((raw / 'nri_wildfire_county_fields.json').read_text(encoding='utf-8'))
    combined = [r.get('attributes', r) for r in combined]
    if rows != combined:
        raise AssertionError('Archived combined rows differ from paginated responses')
    national = [r for r in rows if r['STATEABBRV'] in STATES]
    if len(national) != 3144 or len({r['STCOFIPS'] for r in national}) != 3144:
        raise AssertionError('Expected 3,144 unique records for 50 states and DC')
    if not all(isinstance(r['WFIR_EALB'], (int, float)) and math.isfinite(r['WFIR_EALB']) and r['WFIR_EALB'] >= 0 for r in national):
        raise AssertionError('Missing, negative or nonfinite building-loss value')
    totals = {
        'United States': sum(r['WFIR_EALB'] for r in national),
        'California': sum(r['WFIR_EALB'] for r in national if r['STATEABBRV'] == 'CA'),
        'Los Angeles County': sum(r['WFIR_EALB'] for r in national if r['STCOFIPS'] == '06037'),
    }
    expected = {'United States': 3674507475.328936, 'California': 1706431467.3970764, 'Los Angeles County': 148555889.61651185}
    if not all(abs(totals[k] - v) < .0001 for k, v in expected.items()):
        raise AssertionError('Archived baseline aggregation changed')
    out = ROOT / 'data/derived'
    out.mkdir(exist_ok=True, parents=True)
    result = {
        'version': 'December 2025 1.20.0', 'retrieved_date': '2026-10-25',
        'price_basis': 'December 2024 USD', 'unit': 'US dollars per year',
        'raw_counties_and_equivalents': len(rows), 'counties': len(national),
        'geographic_scope': '50 states and District of Columbia',
        'annual_building_value_eal': totals,
        'checks': {'unique_ids': True, 'nonnegative_finite_values': True, 'paginated_and_combined_snapshots_equal': True},
    }
    (out / 'nri_aggregation_results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    with (out / 'nri_county_building_eal.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({k: r[k] for k in FIELDS} for r in national)
    return result

if __name__ == '__main__':
    print(json.dumps(aggregate(), indent=2))
