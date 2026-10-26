# Data and code for Valuing staged research portfolios for wildfire prevention

Author: Vaishnavi Dilip, Independent Student Researcher, Bangalore, India.
Package version: 1.0.0. Prepared 26 October 2026.

This supplement contains one consistent implementation of the economics model,
the archived FEMA county extract, the source provenance, seven manuscript tables,
and all four figures. The numerical workflow runs offline. No account or online
service is needed to reproduce the calculations after obtaining this archive.

## Reproduce

Requirements are Python 3.10 or later and Node.js 18 or later. Matplotlib is the
only additional Python package required for figure generation. Install it in
your own environment with `python -m pip install -r requirements.txt`.

From the extracted archive directory, run:

```bash
python run_all.py
```

To check the numerical model without plotting dependencies:

```bash
python run_all.py --skip-figures
```

If Node.js is not on the command search path, use `--node PATH_TO_NODE`. The
runner checks the raw data, reaggregates the FEMA baseline, executes the single
JavaScript model, exports its results, verifies the rounded manuscript tables,
and regenerates the four figures as PNG, SVG and PDF. It writes a concise
verification record to `outputs/verification.json`. There are no network calls.

The verified preparation environment used Python 3.12.14, Node.js v24.22.1 and
Matplotlib 3.10.8. Numerical comparisons use tolerances suited to floating-point
arithmetic and displayed precision. Font substitution and graphics-library
versions can change image layout; PDF/SVG timestamps or identifiers can change
file hashes without changing the analysis.

## Contents

- `code/aggregate_fema.py`: rebuilds the national and California loss baselines
  from the two unmodified paginated source responses.
- `code/wildfire_economics_model.js`: the complete portfolio, deployment,
  performance-threshold, cost-target, cash-budget and information-value model.
- `code/export_results.py`: exports the model results to readable CSV files.
- `code/verify_tables.py`: verifies rounded numerical values in the seven tables.
- `code/plot_figures.py`: regenerates the figures from the same model outputs.
- `data/raw/`: paginated FEMA responses, their combined row snapshot, and source
  item metadata. Source records retain their original fields.
- `data/derived/`: the 3,144-row analysis CSV and aggregate baseline results.
- `outputs/`: full-precision model JSON, numerical CSV exports and verification.
- `tables/`: exact CSV transcriptions of manuscript Tables 1–7.
- `figures/`: the four manuscript figures in PNG, SVG and PDF formats.
- `provenance/`: FEMA retrieval URLs, field and price-basis notes, the extraction
  verification script, source terms and bibliographic references.
- `repository/`: prepared deposit metadata and a publication checklist.
- `CITATION.cff`: author and version metadata. No DOI has been assigned to this
  prepared package; the repository-issued DOI must be added after deposit.

## Data and accounting

FEMA National Risk Index version 1.20.0 (December 2025) was retrieved on
25 October 2026. The public county view is identified in
`provenance/fema_source_notes.json`; the two exact query URLs and retained source
metadata are included. The extraction contains 3,232 unique county/equivalent
records. Filtering to the 50 states and District of Columbia retains 3,144
records, with no missing, negative or nonfinite `WFIR_EALB` values. Summing each
county once gives:

| Geography | Modelled annual building-value loss in US dollars |
|---|---:|
| United States, 50 states and DC | 3,674,507,475.328936 |
| California | 1,706,431,467.3970764 |

These values have a December 2024 price basis. California is a subset of the
national total and is not added to it. `WFIR_EALB` is building-value expected
annual loss; it is not observed damage, insured payouts, suppression expenditure,
or total social cost. Other fields in the unmodified source responses are not
substituted for that accounting boundary. The raw files retain the broader
source schema to support provenance, not to expand the paper's benefit account.

## Model interpretation

All deployment costs, scientific probabilities, adoption, maturity profiles and
effectiveness values are illustrative. The 0.6-year commissioning ratio is a
low-cost worked example, not a measured vegetation cost. Adoption is a share of
expected annual loss associated with covered eligible exposures, not a share of
land area. Prospective money is in constant December 2024 dollars. Discounting
applies to research stages and to each commissioning, maintenance and benefit
cash flow. Undiscounted cash-budget outputs are also constant-dollar amounts.

At the specified 15% effectiveness, the maximum commissioning-cost ratio for
positive expected value is below 1.0793002 years of covered annual loss. Matching
a 2:1 mitigation alternative requires a ratio below 0.4395350 years. Equality
denotes indifference. Both depend on the stated research design, loss-weighted
adoption, maintenance, timing and scientific success probability.

The reconstructed external 4.4–13.2-year cost ratios are stress-test anchors from
a different insured-loss account. They are not measured plant costs or a
like-for-like technology comparison. The 75–92% ratio difference is a required
cost-efficiency target under the assumptions, not demonstrated cost savings.

At the worked-example 0.6-year ratio, the conditional maximum expected research
present value is US$60,414,698.05884292, holding discovery probability and
deployment performance fixed. This is not an annual appropriation, an optimal
national budget or a spending response estimate. Subtracting the programme's
US$11,684,652.250745 research cost gives the already-reported US$48,730,045.808098
NPV; that difference must not be counted as a separate benefit. The same
deployment cannot match the 2:1 alternative even with zero research cost.

The information-value example evaluates a different candidate and is not added
to portfolio NPV. Expected deployment spending withheld differs from welfare
value. Sensitivity settings are stress tests, not confidence intervals or fitted
probability distributions.

## Figures and tables

Figure 1 shows portfolio value versus project count and technical dependence.
Figure 2 shows commissioning-cost and adoption frontiers, including the 4.4,
8.8 and 13.2-year cost stress tests. Figure 3 shows one-at-a-time sensitivity
ranges from Table 6. Figure 4 separates validation value from deployment
spending. Table 5 reports the commissioning-cost stress-test comparison.

## Rights and citation

FEMA source materials remain governed by the source terms reproduced in
`provenance/FEMA_TERMS.txt`; they are not relicensed by this package. Licenses for
the author's code and documentation have not yet been finalized. MIT for code
and CC BY 4.0 for original documentation are proposed in the deposit checklist;
neither grant is asserted by this prepared archive. Original copyrighted
research reports are not redistributed; citations link to the publishers.

This product uses the Federal Emergency Management Agency's National Risk Index
dataset API or downloadable datasets but is not endorsed by FEMA. The Federal
Government or FEMA cannot vouch for the data or analyses derived from these data
after the data have been retrieved from the Agency's website(s).
