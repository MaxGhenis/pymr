"""Tests for individual MR methods."""

import numpy as np
import pytest

from pymr.methods import simple_mode, weighted_mode


class TestSimpleMode:
    """Test simple mode-based MR estimation."""

    def test_simple_mode_basic(self):
        """Simple mode should find peak of Wald ratio distribution."""
        # Create data where most SNPs have Wald ratio ~0.5
        beta_exp = np.array([0.1, 0.2, 0.15, 0.12, 0.18, 0.14, 0.16])
        se_exp = np.array([0.01] * 7)
        beta_out = np.array([0.05, 0.10, 0.075, 0.06, 0.09, 0.07, 0.08])
        se_out = np.array([0.02] * 7)

        result = simple_mode(beta_exp, se_exp, beta_out, se_out)

        assert "beta" in result
        assert "se" in result
        assert "pval" in result
        # Mode should be around 0.5
        assert 0.4 < result["beta"] < 0.6

    def test_simple_mode_custom_bandwidth(self):
        """Simple mode should accept custom bandwidth."""
        beta_exp = np.array([0.1, 0.2, 0.15])
        se_exp = np.array([0.01] * 3)
        beta_out = np.array([0.05, 0.10, 0.075])
        se_out = np.array([0.02] * 3)

        result = simple_mode(beta_exp, se_exp, beta_out, se_out, bandwidth=0.1)

        assert "beta" in result
        assert result["nsnp"] == 3


class TestWeightedMode:
    """Test weighted mode-based MR estimation."""

    def test_weighted_mode_basic(self):
        """Weighted mode should weight by inverse variance."""
        # Create data where most SNPs have Wald ratio ~0.5
        beta_exp = np.array([0.1, 0.2, 0.15, 0.12, 0.18, 0.14, 0.16])
        se_exp = np.array([0.01] * 7)
        beta_out = np.array([0.05, 0.10, 0.075, 0.06, 0.09, 0.07, 0.08])
        se_out = np.array([0.02] * 7)

        result = weighted_mode(beta_exp, se_exp, beta_out, se_out)

        assert "beta" in result
        assert "se" in result
        assert "pval" in result
        assert "nsnp" in result
        # Mode should be around 0.5
        assert 0.4 < result["beta"] < 0.6
        assert result["nsnp"] == 7

    def test_weighted_mode_uses_inverse_variance_weights(self):
        """Weighted mode should use inverse variance weights in KDE."""
        # Create data with varying precision
        beta_exp = np.array([0.1, 0.2, 0.15, 0.12, 0.18])
        se_exp = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        beta_out = np.array([0.05, 0.10, 0.075, 0.06, 0.09])
        # Vary the SE for outcome
        se_out = np.array([0.02, 0.01, 0.02, 0.03, 0.02])

        result = weighted_mode(beta_exp, se_exp, beta_out, se_out)

        # Should return valid results
        assert "beta" in result
        assert "se" in result
        assert "pval" in result
        # Result should be a valid estimate
        assert 0.3 < result["beta"] < 0.7

    def test_weighted_mode_custom_bandwidth(self):
        """Weighted mode should accept custom bandwidth."""
        beta_exp = np.array([0.1, 0.2, 0.15])
        se_exp = np.array([0.01] * 3)
        beta_out = np.array([0.05, 0.10, 0.075])
        se_out = np.array([0.02] * 3)

        result = weighted_mode(beta_exp, se_exp, beta_out, se_out, bandwidth=0.1)

        assert "beta" in result
        assert result["nsnp"] == 3

    def test_weighted_mode_returns_odds_ratio(self):
        """Weighted mode should include OR and confidence interval."""
        beta_exp = np.array([0.1, 0.2, 0.15])
        se_exp = np.array([0.01] * 3)
        beta_out = np.array([0.05, 0.10, 0.075])
        se_out = np.array([0.02] * 3)

        result = weighted_mode(beta_exp, se_exp, beta_out, se_out)

        assert "OR" in result
        assert "OR_lci" in result
        assert "OR_uci" in result
        assert result["OR"] == pytest.approx(np.exp(result["beta"]))
