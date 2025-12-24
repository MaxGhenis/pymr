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


def mr_presso(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    n_simulations: int = 10000,
    outlier_test: bool = True,
    distortion_test: bool = True,
) -> dict[str, Any]:
    """MR-PRESSO (Pleiotropy RESidual Sum and Outlier).

    Detects and corrects for horizontal pleiotropy via:
    1. Global test: Tests for presence of pleiotropy
    2. Outlier test: Identifies SNPs with significant residuals
    3. Distortion test: Tests if removing outliers changes estimate

    Args:
        beta_exp: Effect sizes for exposure (per allele)
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome (per allele)
        se_out: Standard errors for outcome
        n_simulations: Number of simulations for global test
        outlier_test: Whether to perform outlier detection
        distortion_test: Whether to test for distortion

    Returns:
        Dictionary with:
            - global_test_pval: p-value for presence of horizontal pleiotropy
            - outlier_indices: list of detected outlier indices
            - corrected_beta: IVW estimate after outlier removal
            - corrected_se: SE after outlier removal
            - corrected_pval: p-value after outlier removal
            - distortion_test_pval: p-value for significant difference
            - original_beta: Original IVW estimate
            - original_se: Original IVW SE
            - nsnp: Number of SNPs

    Raises:
        ValueError: If fewer than 3 SNPs provided

    References:
        Verbanck et al. (2018) Nature Genetics 50:693-698
    """
    if len(beta_exp) < 3:
        msg = "MR-PRESSO requires at least 3 SNPs"
        raise ValueError(msg)

    # Get original IVW estimate
    original_ivw = ivw(beta_exp, se_exp, beta_out, se_out)
    original_beta = original_ivw["beta"]
    original_se = original_ivw["se"]

    # Compute observed residual sum of squares
    wald_ratio = beta_out / beta_exp
    wald_se = np.abs(se_out / beta_exp)
    weights = 1 / wald_se**2

    residuals = wald_ratio - original_beta
    rss_obs = np.sum((residuals**2) * weights)

    # Global test: Simulate null distribution
    # Use legacy RandomState for reproducibility with np.random.seed()
    rng = np.random.RandomState()
    rss_null = np.zeros(n_simulations)

    for i in range(n_simulations):
        # Simulate under null (no pleiotropy)
        sim_wald = rng.normal(original_beta, wald_se)
        sim_residuals = sim_wald - original_beta
        rss_null[i] = np.sum((sim_residuals**2) * weights)

    # Global test p-value
    global_test_pval = float(np.mean(rss_null >= rss_obs))

    # Outlier test
    outlier_indices: list[int] = []
    if outlier_test:
        # Compute residuals and test each SNP
        for idx in range(len(beta_exp)):
            # Compute RSS without this SNP
            mask = np.ones(len(beta_exp), dtype=bool)
            mask[idx] = False

            # IVW without this SNP
            ivw_loo = ivw(
                beta_exp[mask],
                se_exp[mask],
                beta_out[mask],
                se_out[mask]
            )
            beta_loo = ivw_loo["beta"]

            # Residual for this SNP
            residual_i = wald_ratio[idx] - beta_loo

            # Simulate null distribution for this SNP's residual
            rss_null_i = np.zeros(n_simulations)
            for sim_idx in range(n_simulations):
                sim_wald_i = rng.normal(beta_loo, wald_se[idx])
                sim_residual_i = sim_wald_i - beta_loo
                rss_null_i[sim_idx] = (sim_residual_i**2) * weights[idx]

            # Test if observed residual is extreme
            pval_i = np.mean(rss_null_i >= (residual_i**2) * weights[idx])

            # Bonferroni correction
            if pval_i < (0.05 / len(beta_exp)):
                outlier_indices.append(idx)

    # Corrected estimate (after outlier removal)
    if len(outlier_indices) > 0:
        keep_mask = np.ones(len(beta_exp), dtype=bool)
        keep_mask[outlier_indices] = False

        corrected_ivw = ivw(
            beta_exp[keep_mask],
            se_exp[keep_mask],
            beta_out[keep_mask],
            se_out[keep_mask]
        )
        corrected_beta = corrected_ivw["beta"]
        corrected_se = corrected_ivw["se"]
        corrected_pval = corrected_ivw["pval"]
    else:
        corrected_beta = original_beta
        corrected_se = original_se
        corrected_pval = original_ivw["pval"]

    # Distortion test
    distortion_test_pval = np.nan
    if distortion_test and len(outlier_indices) > 0:
        # Test if difference between original and corrected is significant
        diff = abs(corrected_beta - original_beta)
        se_diff = np.sqrt(original_se**2 + corrected_se**2)
        z_stat = diff / se_diff if se_diff > 0 else 0
        distortion_test_pval = float(2 * stats.norm.sf(abs(z_stat)))

    return {
        "global_test_pval": global_test_pval,
        "outlier_indices": outlier_indices,
        "corrected_beta": float(corrected_beta),
        "corrected_se": float(corrected_se),
        "corrected_pval": float(corrected_pval),
        "distortion_test_pval": float(distortion_test_pval),
        "original_beta": float(original_beta),
        "original_se": float(original_se),
        "nsnp": len(beta_exp),
    }
