# Model definitions and units

The JavaScript model is the single source of the numerical scenario results.
All programme money is constant December 2024 US dollars, except the separate
information example, whose money is present-value US$ millions at a common
decision date. The value of information is not added to portfolio value.

Research payments occur at years 0, 1 and 3. The initial payment is US$0.25m;
25% of projects proceed to a US$1m payment; a fraction `p/0.25` of that group
proceeds to the US$2m completion payment. Expected project cost is
`cbar = 0.25m + 0.25 × 1m/(1+d) + p × 2m/(1+d)^3`.
For `N` projects, expected research PV is `C = N × cbar`.

Projects are parallel and substitutable. Their benefits cannot be added over
the same loss pool. Independence gives `P = 1 − (1−p)^N`; the beta-binomial
scenario retains marginal success `p` while varying positive dependence.
The programme does not cancel other projects after one successful result.

For commissioning year `T` and `H` subsequent benefit years,
`F = sum((1+d)^−(T+j))` and `G = sum(g_j × (1+d)^−(T+j))`, for `j=1,...,H`.
Commissioning cost is `k0 × a × L`; annual maintenance is `m × a × L`.
Here `L` is annual baseline building loss, `a` is its covered eligible share,
`k0` has units of years, and `m` is dimensionless.
The deployment PV is `D = (k0/(1+d)^T + mF) × aL = kappa × aL`.
Conditional deployment value is `V = aL × (Gr − kappa)` and
portfolio NPV is `W = P × max(V,0) − C`.

For positive `N`, `P`, and `G`, required effectiveness is
`rmin = kappa/G + C/(PLaG)`.
The inverse commissioning-cost boundary is
`k0max = (1+d)^T × [Gr − mF − C/(PaL)]`.
At equality, expected NPV is zero; positive value requires lower commissioning
cost. A negative boundary means no nonnegative commissioning cost suffices.
For a conventional alternative with benefit–cost ratio `b` and equal expected
resources, replace `Gr` by `Gr/b` in the inverse commissioning-cost boundary.

The conditional research ceiling is `Cmax = P × max(V,0)`, evaluated while
holding the discovery probability and deployment outcome fixed. Research
spending is not assumed capable of leaving scientific success unchanged in
practice; this is a screening allowance, not a calibrated response to funding.
The allowance against the alternative is `P × (aLGr/b − D)`.
A negative allowance means even zero research cost cannot make that deployment
competitive. Truncating it to zero must not be interpreted as feasibility.

The cost-comparison scenarios use rounded ratios 4.4, 8.8 and 13.2 years as
stress-test inputs. Their source scope differs from FEMA building-value loss.
They do not establish attainable cost reductions for vegetation research.

When risk-estimation uncertainty multiplies `L` by `f` for the same physical
deployment, `k0` and `m` are divided by `f`; dollar commissioning and maintenance
costs therefore remain fixed. Leaving the ratios unchanged would model a
different programme whose spending changes with the loss estimate.

No fitted probability distributions are assigned to uncertain deployment inputs.
Best-portfolio searches enumerate integer `N` from 0 to 200. Sensitivity ranges
are one-at-a-time stress tests, except for linked changes needed to retain a
consistent physical programme or research-stage probability tree.
