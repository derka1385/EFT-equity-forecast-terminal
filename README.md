# EFT — Equity Forecast Terminal

A browser-based equity risk terminal: it calibrates a volatility model on a stock's daily price history and simulates thousands of future price paths to estimate the range of outcomes and the downside risk.

**Live demo:** https://derka1385.github.io/EFT-equity-forecast-terminal/

> Educational project. Not investment advice.

## What it does

1. Loads daily prices for a ticker. About 65 common tickers (US and European stocks, indices, crypto, FX) come from a daily Yahoo Finance snapshot published with the site by GitHub Actions; any other ticker is fetched live through public CORS relays.
2. Calibrates the model on historical log-returns.
3. Runs a Monte Carlo simulation (20,000 paths by default, adjustable from 5,000 to 50,000).
4. Reports risk metrics from the simulated terminal-price distribution:
   - 95% Value-at-Risk and 95% Expected Shortfall (CVaR)
   - probability of loss
   - P5–P95 percentile price bands
   - a Forecast Reliability Index (0–100)

## Model (v7)

| Component | Specification |
|---|---|
| Drift | Bayesian posterior mean, shrunk toward a prior and toward zero (short-horizon expected returns are very noisy); AR(1) return dynamics |
| Volatility | GJR-GARCH(1,1): negative shocks raise future volatility more than positive ones |
| Shocks | Standardised Student-t, degrees of freedom calibrated by likelihood (fatter tails than Gaussian GBM) |
| Regimes | 3-state semi-Markov regime model: the probability of leaving a regime depends on how long it has lasted; regimes are propagated with sequential Monte Carlo particles |
| Diagnostics | RiskMetrics EWMA volatility (λ = 0.94) vs historical volatility, used in the reliability index |

## Research lineage

- Engle (1982), ARCH
- Bollerslev (1986, 1987), GARCH and Student-t GARCH
- Glosten, Jagannathan & Runkle (1993), asymmetric volatility
- Hansen (1994), conditional Student-t density
- J.P. Morgan RiskMetrics (1996), EWMA volatility
- Welch & Goyal (2008, updated 2024), limits of out-of-sample equity-return predictability

## Limitations

- Daily prices alone do not make individual-stock returns reliably predictable. The model improves the calibration of volatility and tails; it does not create a directional edge.
- No walk-forward backtest yet. That is the next step.
- Tickers outside the daily snapshot depend on free public relays, which can be slow or unavailable.

## Documentation

- `EFT_model_documentation.pdf`: 10-page technical paper on the core model (v5: GBM, Bayesian calibration, AR(1) drift, VaR/CVaR).
- The v6–v7 extensions (GJR-GARCH, Student-t, regime switching) are documented inside the app.

## Stack

Single HTML file, vanilla JavaScript, Chart.js. No build step.

## Author

Nolann Petri, BSc Business & Economics, Stockholm School of Economics.
