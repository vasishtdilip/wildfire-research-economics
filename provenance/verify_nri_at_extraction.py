"""Reproduce the county building-value EAL aggregation from archived FEMA data."""
from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parent
states=set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split())
raw=json.loads((R/'nri_wildfire_county_fields.json').read_text())
if isinstance(raw,dict):rows=[f.get('attributes',f) for f in raw.get('features',raw.get('rows',[]))]
else:rows=[f.get('attributes',f) for f in raw]
national=[r for r in rows if r['STATEABBRV'] in states]
assert len(national)==3144
assert len({r['STCOFIPS'] for r in national})==3144
assert all(r['WFIR_EALB'] is not None and r['WFIR_EALB']>=0 for r in national)
totals={name:sum(r['WFIR_EALB'] for r in national if cond(r)) for name,cond in [('United States',lambda r:True),('California',lambda r:r['STATEABBRV']=='CA'),('Los Angeles County',lambda r:r['STCOFIPS']=='06037')]}
assert abs(totals['United States']-3674507475.328936)<.01
(R/'nri_aggregation_results.json').write_text(json.dumps({'version':'December 2025 1.20.0','price_basis':'December 2024 USD','counties':len(national),'annual_building_value_eal':totals},indent=2))
with (R/'nri_county_building_eal.csv').open('w') as f:
    fields=['STATE','STATEABBRV','COUNTY','STCOFIPS','WFIR_EALB','NRI_VER']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k) for k in fields} for r in national)
print(json.dumps(totals,indent=2))
