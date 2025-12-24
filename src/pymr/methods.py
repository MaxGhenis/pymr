"""Mendelian Randomization statistical methods.

This module implements the core MR estimators:
- IVW (Inverse Variance Weighted)
- Weighted Median
- MR-Egger
- Mode-based estimation

References:
    Burgess S, Thompson SG (2015). Mendelian Randomization: Methods for Using
    Genetic Variants in Causal Estimation. Chapman & Hall/CRC.
"""

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import stats


def ivw(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
) -> dict[str, float]:
    """Inverse Variance Weighted MR.

    Computes a weighted average of per-SNP Wald ratios, where weights
    are the inverse of the outcome variance.

    Args:
        beta_exp: Effect sizes for exposure (per allele)
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome (per allele)
        se_out: Standard errors for outcome

    Returns:
        Dictionary with beta, se, pval, OR, OR_lci, OR_uci, nsnp
    """
    # Wald ratios
    wald_ratio = beta_out / beta_exp
    wald_se = np.abs(se_out / beta_exp)

    # IVW weights
    weights = 1 / wald_se**2

    # Weighted mean
    beta = np.sum(wald_ratio * weights) / np.sum(weights)
    se = np.sqrt(1 / np.sum(weights))
    pval = 2 * stats.norm.sf(np.abs(beta / se))

    return {
        "beta": float(beta),
        "se": float(se),
        "pval": float(pval),
        "OR": float(np.exp(beta)),
        "OR_lci": float(np.exp(beta - 1.96 * se)),
        "OR_uci": float(np.exp(beta + 1.96 * se)),
        "nsnp": len(beta_exp),
    }


def weighted_median(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    n_bootstrap: int = 1000,
) -> dict[str, float]:
    """Weighted Median MR.

    Robust to up to 50% of instruments being invalid.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        n_bootstrap: Number of bootstrap samples for SE estimation

    Returns:
        Dictionary with beta, se, pval, OR, OR_lci, OR_uci, nsnp

    Raises:
        ValueError: If fewer than 3 SNPs provided
    """
    if len(beta_exp) < 3:
        msg = "Weighted median requires at least 3 SNPs"
        raise ValueError(msg)

    # Wald ratios and weights
    wald_ratio = beta_out / beta_exp
    wald_se = np.abs(se_out / beta_exp)
    weights = 1 / wald_se**2

    # Weighted median
    sorted_idx = np.argsort(wald_ratio)
    cumsum_weights = np.cumsum(weights[sorted_idx]) / np.sum(weights)
    median_idx = np.searchsorted(cumsum_weights, 0.5)
    beta = float(wald_ratio[sorted_idx[median_idx]])

    # Bootstrap SE
    rng = np.random.default_rng(42)
    betas = []
    for _ in range(n_bootstrap):
        idx = rng.choice(len(beta_exp), size=len(beta_exp), replace=True)
        w = weights[idx]
        r = wald_ratio[idx]
        sidx = np.argsort(r)
        cs = np.cumsum(w[sidx]) / np.sum(w)
        midx = np.searchsorted(cs, 0.5)
        betas.append(r[sidx[midx]])

    se = max(float(np.std(betas)), 1e-10)  # Avoid division by zero
    pval = 2 * stats.norm.sf(np.abs(beta / se))

    return {
        "beta": beta,
        "se": se,
        "pval": float(pval),
        "OR": float(np.exp(beta)),
        "OR_lci": float(np.exp(beta - 1.96 * se)),
        "OR_uci": float(np.exp(beta + 1.96 * se)),
        "nsnp": len(beta_exp),
    }


def mr_egger(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
) -> dict[str, float]:
    """MR-Egger regression.

    Tests for and corrects directional pleiotropy. A non-zero intercept
    indicates the presence of directional pleiotropy.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome

    Returns:
        Dictionary with beta, se, pval, intercept, intercept_se,
        intercept_pval, OR, OR_lci, OR_uci, nsnp
    """
    # Ensure positive exposure effects (InSIDE assumption)
    sign = np.sign(beta_exp)
    beta_exp_oriented = np.abs(beta_exp)
    beta_out_oriented = beta_out * sign

    # Weighted regression
    weights = 1 / se_out**2
    W = np.diag(weights)
    X = np.column_stack([np.ones(len(beta_exp)), beta_exp_oriented])

    # Solve normal equations
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ beta_out_oriented

    try:
        coef = np.linalg.solve(XtWX, XtWy)
        residuals = beta_out_oriented - X @ coef
        n = len(beta_exp)
        sigma2 = np.sum((residuals**2) * weights) / (n - 2)
        var_coef = sigma2 * np.linalg.inv(XtWX)
        se_coef = np.sqrt(np.diag(var_coef))
    except np.linalg.LinAlgError:
        # Fallback for singular matrices
        coef = np.array([0.0, np.mean(beta_out / beta_exp)])
        se_coef = np.array([np.nan, np.nan])

    intercept = float(coef[0])
    intercept_se = max(float(se_coef[0]), 1e-10)  # Avoid division by zero
    beta = float(coef[1])
    se = max(float(se_coef[1]), 1e-10)  # Avoid division by zero

    intercept_pval = 2 * stats.norm.sf(np.abs(intercept / intercept_se))
    pval = 2 * stats.norm.sf(np.abs(beta / se))

    return {
        "beta": beta,
        "se": se,
        "pval": float(pval),
        "intercept": intercept,
        "intercept_se": intercept_se,
        "intercept_pval": float(intercept_pval),
        "OR": float(np.exp(beta)),
        "OR_lci": float(np.exp(beta - 1.96 * se)),
        "OR_uci": float(np.exp(beta + 1.96 * se)),
        "nsnp": len(beta_exp),
    }


def simple_mode(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    bandwidth: float | None = None,
) -> dict[str, float]:
    """Mode-based MR estimation.

    Consistent when the largest group of SNPs share the same causal effect.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        bandwidth: Kernel bandwidth (None for automatic)

    Returns:
        Dictionary with beta, se, pval, OR, OR_lci, OR_uci, nsnp
    """
    wald_ratio = beta_out / beta_exp

    # Silverman's rule of thumb for bandwidth
    if bandwidth is None:
        n = len(wald_ratio)
        iqr = np.percentile(wald_ratio, 75) - np.percentile(wald_ratio, 25)
        bandwidth = 0.9 * min(np.std(wald_ratio), iqr / 1.34) * n ** (-0.2)

    # Kernel density estimation on a grid
    grid = np.linspace(
        np.min(wald_ratio) - 3 * bandwidth,
        np.max(wald_ratio) + 3 * bandwidth,
        1000,
    )
    density = np.zeros_like(grid)
    for r in wald_ratio:
        density += stats.norm.pdf(grid, loc=r, scale=bandwidth)

    beta = float(grid[np.argmax(density)])

    # Bootstrap SE (simplified)
    rng = np.random.default_rng(42)
    betas = []
    for _ in range(1000):
        idx = rng.choice(len(beta_exp), size=len(beta_exp), replace=True)
        wr = (beta_out[idx] / beta_exp[idx])
        d = np.zeros_like(grid)
        for r in wr:
            d += stats.norm.pdf(grid, loc=r, scale=bandwidth)
        betas.append(grid[np.argmax(d)])

    se = float(np.std(betas))
    pval = 2 * stats.norm.sf(np.abs(beta / se)) if se > 0 else 1.0

    return {
        "beta": beta,
        "se": se,
        "pval": float(pval),
        "OR": float(np.exp(beta)),
        "OR_lci": float(np.exp(beta - 1.96 * se)),
        "OR_uci": float(np.exp(beta + 1.96 * se)),
        "nsnp": len(beta_exp),
    }
