# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyMR is a modern Python package for Mendelian Randomization (MR) analysis. It provides frequentist and Bayesian MR methods, sensitivity analyses, data harmonization, and GWAS data integration - all in pure Python without external dependencies like PLINK, PyMC, or Stan.

Published on PyPI as `pymr-genetics`.

## Development Commands

```bash
# Install in development mode
pip install -e ".[dev,docs]"

# Run all tests with coverage
pytest

# Run a single test file
pytest tests/test_mr.py

# Run a specific test
pytest tests/test_mr.py::TestIVW::test_ivw_basic

# Linting
ruff check src tests
ruff format src tests

# Type checking
mypy src/pymr

# Build documentation
jupyter-book build docs
```

### React Demo App (app/)

```bash
cd app
bun install
bun run dev      # Development server
bun run build    # Production build
bun run lint     # ESLint
```

## Architecture

### Python Package (src/pymr/)

The package follows a modular design with clear separation of concerns:

- **mr.py**: Main `MR` class that orchestrates analyses. Accepts harmonized data with columns `beta_exp`, `se_exp`, `beta_out`, `se_out` and runs multiple methods via `MR.run()`. Provides `heterogeneity()` and `leave_one_out()` sensitivity analyses.

- **methods.py**: Core MR estimators - `ivw`, `weighted_median`, `mr_egger`, `simple_mode`, `weighted_mode`, `mr_presso`, `mr_raps`, `contamination_mixture`. Each returns a dict with `beta`, `se`, `pval`, `OR`, `OR_lci`, `OR_uci`, `nsnp`.

- **harmonize.py**: `harmonize()` function aligns exposure/outcome GWAS data by matching SNPs, flipping effect sizes for misaligned alleles, and handling palindromic SNPs (A/T, C/G).

- **io.py**: `load_gwas()` loads summary statistics from files, auto-detecting Pan-UKB and IEU OpenGWAS formats.

- **api.py**: Integration with external GWAS databases - IEU OpenGWAS API, Pan-UK Biobank, GWAS Catalog, FinnGen.

- **sensitivity.py**: Additional sensitivity analyses - `steiger_filtering`, `cochrans_q`, `rucker_q`, `funnel_asymmetry`.

- **bayesian.py**: `BayesianMR` class for full posterior inference with Metropolis-Hastings sampling.

- **multivariable.py**: `MultivariableMR` for analyses with multiple exposures.

- **clumping.py**: LD clumping utilities - `ld_clump`, `get_ld_matrix`.

- **plots.py**: Visualization functions for forest plots, scatter plots, funnel plots.

### Key Data Flow

1. Load GWAS data via `load_gwas()` or API functions
2. Harmonize exposure/outcome with `harmonize()` (aligns alleles, flips betas)
3. Run MR analysis with `MR(harmonized_data).run()` or individual method functions
4. Perform sensitivity analyses (heterogeneity, leave-one-out, MR-PRESSO)

### React Demo (app/)

Interactive web demo built with Vite + React + TypeScript. Components in `app/src/components/` demonstrate MR concepts with visualizations using Recharts.

## Testing

Tests follow TDD approach. Test file structure mirrors source:
- `tests/test_mr.py` - Tests for MR class and individual methods

The test fixtures create synthetic harmonized data with columns expected by MR methods. Tests verify both statistical correctness and proper error handling.

## CI/CD

GitHub Actions runs on Python 3.9-3.12:
- Linting (ruff check + format)
- Type checking (mypy)
- Tests with coverage (pytest + codecov)
- Documentation build (jupyter-book)
