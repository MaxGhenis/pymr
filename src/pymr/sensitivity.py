"""Sensitivity analyses for Mendelian Randomization.

This module implements sensitivity analyses to test MR assumptions:
- Steiger filtering (directionality test)
- Heterogeneity tests
- Pleiotropy tests
"""

from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import stats


def steiger_filtering(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    n_exp: int,
    n_out: int,
    r2_thresh: float = 0.0,
) -> dict[str, Any]:
    """Steiger directionality test and filtering.

    Tests whether the genetic variants explain more variance in the
    exposure than the outcome, as expected under the causal model.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        n_exp: Sample size for exposure GWAS
        n_out: Sample size for outcome GWAS
        r2_thresh: Minimum R² difference threshold for filtering

    Returns:
        Dictionary with:
            - r2_exp: Variance explained in exposure
            - r2_out: Variance explained in outcome
            - correct_direction: Boolean array (True = exp > out)
            - steiger_pval: P-value for directionality test
            - filtered_indices: Indices of SNPs with correct direction
    """
    # Calculate R² for each SNP
    # R² ≈ beta² / (beta² + se² * n)  [approximation for GWAS]
    r2_exp = beta_exp**2 / (beta_exp**2 + se_exp**2 * n_exp)
    r2_out = beta_out**2 / (beta_out**2 + se_out**2 * n_out)

    # Correct direction: SNP explains more variance in exposure
    correct_direction = r2_exp > r2_out + r2_thresh

    # Steiger test: compare total R² using z-test
    total_r2_exp = np.sum(r2_exp)
    total_r2_out = np.sum(r2_out)

    # Fisher's z transformation for correlation comparison
    z_exp = 0.5 * np.log((1 + np.sqrt(total_r2_exp)) / (1 - np.sqrt(total_r2_exp) + 1e-10))
    z_out = 0.5 * np.log((1 + np.sqrt(total_r2_out)) / (1 - np.sqrt(total_r2_out) + 1e-10))

    z_diff = (z_exp - z_out) / np.sqrt(1 / (n_exp - 3) + 1 / (n_out - 3))
    steiger_pval = 2 * stats.norm.sf(np.abs(z_diff))

    return {
        "r2_exp": r2_exp,
        "r2_out": r2_out,
        "r2_exp_total": float(total_r2_exp),
        "r2_out_total": float(total_r2_out),
        "correct_direction": correct_direction,
        "n_correct": int(np.sum(correct_direction)),
        "n_incorrect": int(np.sum(~correct_direction)),
        "steiger_pval": float(steiger_pval),
        "direction_correct": total_r2_exp > total_r2_out,
        "filtered_indices": np.where(correct_direction)[0],
    }


def cochrans_q(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    causal_estimate: float,
) -> dict[str, float]:
    """Cochran's Q test for heterogeneity.

    Tests whether individual SNP estimates are consistent with a
    single causal effect (homogeneity).

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        causal_estimate: The estimated causal effect (e.g., from IVW)

    Returns:
        Dictionary with Q statistic, degrees of freedom, p-value, and I²
    """
    # Wald ratios
    wald_ratio = beta_out / beta_exp
    wald_se = np.abs(se_out / beta_exp)

    # Weights
    weights = 1 / wald_se**2

    # Q statistic
    q = float(np.sum(weights * (wald_ratio - causal_estimate) ** 2))
    df = len(beta_exp) - 1

    # P-value
    q_pval = 1 - float(stats.chi2.cdf(q, df)) if df > 0 else 1.0

    # I² (percentage of variation due to heterogeneity)
    i2 = max(0, (q - df) / q * 100) if q > 0 else 0.0

    return {
        "Q": q,
        "Q_df": df,
        "Q_pval": q_pval,
        "I2": i2,
    }


def rucker_q(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
) -> dict[str, float]:
    """Rucker's Q test comparing IVW vs MR-Egger fit.

    Tests whether allowing an intercept (MR-Egger) significantly
    improves model fit compared to IVW (no intercept).

    A significant difference suggests directional pleiotropy.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome

    Returns:
        Dictionary with Q_IVW, Q_Egger, Q_diff, and p-value
    """
    from pymr.methods import ivw, mr_egger

    # Get IVW estimate
    ivw_result = ivw(beta_exp, se_exp, beta_out, se_out)
    ivw_beta = ivw_result["beta"]

    # Get Egger estimate
    egger_result = mr_egger(beta_exp, se_exp, beta_out, se_out)
    egger_beta = egger_result["beta"]

    # Q statistics
    q_ivw = cochrans_q(beta_exp, se_exp, beta_out, se_out, ivw_beta)
    q_egger = cochrans_q(beta_exp, se_exp, beta_out, se_out, egger_beta)

    # Difference (tests for pleiotropy)
    q_diff = q_ivw["Q"] - q_egger["Q"]
    q_diff_pval = 1 - float(stats.chi2.cdf(q_diff, 1)) if q_diff > 0 else 1.0

    return {
        "Q_IVW": q_ivw["Q"],
        "Q_Egger": q_egger["Q"],
        "Q_diff": q_diff,
        "Q_diff_pval": q_diff_pval,
        "pleiotropy_detected": q_diff_pval < 0.05,
    }


def leave_one_out(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    snp_ids: list[str] | None = None,
    method: str = "IVW",
) -> pd.DataFrame:
    """Leave-one-out sensitivity analysis.

    Reruns the analysis excluding each SNP in turn to identify
    influential observations.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        snp_ids: Optional SNP identifiers
        method: MR method to use ("IVW", "Egger", "Median")

    Returns:
        DataFrame with one row per SNP, showing estimate when excluded
    """
    from pymr.methods import ivw, mr_egger, weighted_median

    methods_map = {
        "IVW": ivw,
        "Egger": mr_egger,
        "Median": weighted_median,
    }

    if method not in methods_map:
        msg = f"Unknown method: {method}. Use one of {list(methods_map.keys())}"
        raise ValueError(msg)

    func = methods_map[method]
    n = len(beta_exp)

    if snp_ids is None:
        snp_ids = [f"SNP_{i}" for i in range(n)]

    results = []
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False

        try:
            result = func(
                beta_exp[mask],
                se_exp[mask],
                beta_out[mask],
                se_out[mask],
            )
            result["excluded_snp"] = snp_ids[i]
            result["excluded_idx"] = i
            results.append(result)
        except (ValueError, np.linalg.LinAlgError):
            # Skip if method fails with one fewer SNP
            pass

    return pd.DataFrame(results)


def single_snp(
    beta_exp: NDArray[np.floating[Any]],
    se_exp: NDArray[np.floating[Any]],
    beta_out: NDArray[np.floating[Any]],
    se_out: NDArray[np.floating[Any]],
    snp_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Single SNP analysis (Wald ratios for each SNP).

    Calculates the causal estimate using each SNP individually.

    Args:
        beta_exp: Effect sizes for exposure
        se_exp: Standard errors for exposure
        beta_out: Effect sizes for outcome
        se_out: Standard errors for outcome
        snp_ids: Optional SNP identifiers

    Returns:
        DataFrame with one row per SNP, showing individual Wald ratio
    """
    n = len(beta_exp)

    if snp_ids is None:
        snp_ids = [f"SNP_{i}" for i in range(n)]

    # Wald ratios
    beta = beta_out / beta_exp
    se = np.abs(se_out / beta_exp)
    pval = 2 * stats.norm.sf(np.abs(beta / se))

    return pd.DataFrame({
        "SNP": snp_ids,
        "beta": beta,
        "se": se,
        "pval": pval,
        "OR": np.exp(beta),
        "OR_lci": np.exp(beta - 1.96 * se),
        "OR_uci": np.exp(beta + 1.96 * se),
    })
