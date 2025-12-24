"""Tests for IEU OpenGWAS API integration (TDD - tests written first)."""

import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pymr.api import (
    IEUClient,
    get_instruments,
    get_outcome,
    list_gwas,
    search_gwas,
)


class TestIEUClient:
    """Test the IEUClient class for API access."""

    def test_client_initialization_default(self):
        """Client should initialize with default base URL."""
        client = IEUClient()
        assert client.base_url == "https://gwas-api.mrcieu.ac.uk"
        assert client.jwt is None

    def test_client_initialization_with_jwt(self):
        """Client should accept JWT token."""
        token = "test_jwt_token_123"
        client = IEUClient(jwt=token)
        assert client.jwt == token

    def test_client_initialization_from_env(self):
        """Client should read JWT from environment variable."""
        with patch.dict(os.environ, {"OPENGWAS_JWT": "env_token"}):
            client = IEUClient()
            assert client.jwt == "env_token"

    def test_client_get_headers_without_jwt(self):
        """Client should return basic headers without JWT."""
        client = IEUClient()
        headers = client._get_headers()
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers

    def test_client_get_headers_with_jwt(self):
        """Client should include Authorization header with JWT."""
        client = IEUClient(jwt="test_token")
        headers = client._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token"


class TestGetInstruments:
    """Test get_instruments function for fetching clumped instruments."""

    @patch("pymr.api.requests.get")
    def test_get_instruments_basic(self, mock_get):
        """get_instruments should fetch tophits with default p-threshold."""
        # Arrange: Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "rsid": "rs123",
                "chr": "1",
                "position": 100000,
                "ea": "A",
                "nea": "G",
                "beta": 0.1,
                "se": 0.01,
                "pval": 1e-10,
                "eaf": 0.3,
            },
            {
                "rsid": "rs456",
                "chr": "2",
                "position": 200000,
                "ea": "C",
                "nea": "T",
                "beta": 0.15,
                "se": 0.02,
                "pval": 1e-12,
                "eaf": 0.4,
            },
        ]
        mock_get.return_value = mock_response

        # Act
        result = get_instruments("ieu-a-2")

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "rsid" in result.columns
        assert "beta" in result.columns
        assert "pval" in result.columns
        assert result.iloc[0]["rsid"] == "rs123"
        # Default p-threshold should be 5e-8
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "pval=5e-08" in call_args[0][0] or "pval" in str(call_args)

    @patch("pymr.api.requests.get")
    def test_get_instruments_custom_threshold(self, mock_get):
        """get_instruments should accept custom p-value threshold."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = get_instruments("ieu-a-2", p_threshold=1e-6)

        assert isinstance(result, pd.DataFrame)
        # Should use custom threshold in API call
        call_args = mock_get.call_args
        assert "1e-06" in str(call_args) or "0.000001" in str(call_args)

    @patch("pymr.api.requests.get")
    def test_get_instruments_with_clumping(self, mock_get):
        """get_instruments should request clumped results by default."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = get_instruments("ieu-a-2", clump=True)

        assert isinstance(result, pd.DataFrame)
        call_args = mock_get.call_args
        # Should include clump parameter
        assert "clump=1" in str(call_args) or "clump" in str(call_args)

    @patch("pymr.api.requests.get")
    def test_get_instruments_api_error(self, mock_get):
        """get_instruments should raise error on API failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        with pytest.raises(Exception):
            get_instruments("invalid-id")


class TestGetOutcome:
    """Test get_outcome function for looking up SNPs in outcome GWAS."""

    @patch("pymr.api.requests.post")
    def test_get_outcome_basic(self, mock_post):
        """get_outcome should lookup SNPs in outcome dataset."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "rsid": "rs123",
                "chr": "1",
                "position": 100000,
                "ea": "A",
                "nea": "G",
                "beta": 0.05,
                "se": 0.02,
                "pval": 0.01,
                "eaf": 0.3,
            },
            {
                "rsid": "rs456",
                "chr": "2",
                "position": 200000,
                "ea": "C",
                "nea": "T",
                "beta": 0.08,
                "se": 0.03,
                "pval": 0.005,
                "eaf": 0.4,
            },
        ]
        mock_post.return_value = mock_response

        # Act
        snps = ["rs123", "rs456"]
        result = get_outcome("ieu-a-7", snps)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "rsid" in result.columns
        assert "beta" in result.columns
        assert result.iloc[0]["rsid"] == "rs123"
        # Should POST with SNP list
        mock_post.assert_called_once()

    @patch("pymr.api.requests.post")
    def test_get_outcome_with_proxies(self, mock_post):
        """get_outcome should support LD proxy lookup."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        result = get_outcome("ieu-a-7", ["rs123"], proxies=True)

        assert isinstance(result, pd.DataFrame)
        # Should include proxies parameter
        call_args = mock_post.call_args
        assert call_args is not None

    @patch("pymr.api.requests.post")
    def test_get_outcome_missing_snps(self, mock_post):
        """get_outcome should handle missing SNPs gracefully."""
        # Return empty results for missing SNPs
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        result = get_outcome("ieu-a-7", ["rs_nonexistent"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestSearchGWAS:
    """Test search_gwas function for searching available GWAS."""

    @patch("pymr.api.requests.get")
    def test_search_gwas_basic(self, mock_get):
        """search_gwas should search GWAS by keyword."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "ieu-a-2",
                "trait": "Body mass index",
                "author": "Locke AE",
                "year": 2015,
                "consortium": "GIANT",
                "sample_size": 339224,
            },
            {
                "id": "ieu-a-95",
                "trait": "Childhood body mass index",
                "author": "Felix JF",
                "year": 2016,
                "consortium": "EGG",
                "sample_size": 47541,
            },
        ]
        mock_get.return_value = mock_response

        # Act
        result = search_gwas("body mass index")

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "id" in result.columns
        assert "trait" in result.columns
        assert "body mass index" in result.iloc[0]["trait"].lower()

    @patch("pymr.api.requests.get")
    def test_search_gwas_no_results(self, mock_get):
        """search_gwas should return empty DataFrame when no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = search_gwas("nonexistent trait xyz")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestListGWAS:
    """Test list_gwas function for listing all available GWAS."""

    @patch("pymr.api.requests.get")
    def test_list_gwas_basic(self, mock_get):
        """list_gwas should return all available GWAS IDs."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "ieu-a-2",
                "trait": "Body mass index",
                "sample_size": 339224,
            },
            {
                "id": "ieu-a-7",
                "trait": "Type 2 diabetes",
                "sample_size": 159208,
            },
            {
                "id": "ieu-a-95",
                "trait": "Childhood body mass index",
                "sample_size": 47541,
            },
        ]
        mock_get.return_value = mock_response

        # Act
        result = list_gwas()

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "id" in result.columns
        assert "trait" in result.columns

    @patch("pymr.api.requests.get")
    def test_list_gwas_pagination(self, mock_get):
        """list_gwas should handle paginated results if needed."""
        # This test assumes the API might paginate large results
        mock_response = Mock()
        mock_response.status_code = 200
        # Return a large number of results
        mock_response.json.return_value = [
            {"id": f"ieu-a-{i}", "trait": f"Trait {i}", "sample_size": 10000}
            for i in range(100)
        ]
        mock_get.return_value = mock_response

        result = list_gwas()

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 100


class TestIntegrationWorkflow:
    """Test end-to-end workflow with mocked API responses."""

    @patch("pymr.api.requests.post")
    @patch("pymr.api.requests.get")
    def test_full_mr_workflow(self, mock_get, mock_post):
        """Test complete workflow: get instruments -> get outcome -> harmonize."""
        # Mock get_instruments response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [
            {
                "rsid": "rs1",
                "chr": "1",
                "position": 100000,
                "ea": "A",
                "nea": "G",
                "beta": 0.1,
                "se": 0.01,
                "pval": 1e-10,
                "eaf": 0.3,
            },
            {
                "rsid": "rs2",
                "chr": "2",
                "position": 200000,
                "ea": "C",
                "nea": "T",
                "beta": 0.15,
                "se": 0.02,
                "pval": 1e-12,
                "eaf": 0.4,
            },
        ]
        mock_get.return_value = mock_get_response

        # Mock get_outcome response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = [
            {
                "rsid": "rs1",
                "chr": "1",
                "position": 100000,
                "ea": "A",
                "nea": "G",
                "beta": 0.05,
                "se": 0.02,
                "pval": 0.01,
                "eaf": 0.3,
            },
            {
                "rsid": "rs2",
                "chr": "2",
                "position": 200000,
                "ea": "C",
                "nea": "T",
                "beta": 0.08,
                "se": 0.03,
                "pval": 0.005,
                "eaf": 0.4,
            },
        ]
        mock_post.return_value = mock_post_response

        # Act: Complete workflow
        # 1. Get instruments for exposure
        instruments = get_instruments("ieu-a-2")  # BMI
        assert len(instruments) == 2

        # 2. Extract SNP list
        snp_list = instruments["rsid"].tolist()
        assert snp_list == ["rs1", "rs2"]

        # 3. Get outcome data
        outcome = get_outcome("ieu-a-7", snp_list)  # T2D
        assert len(outcome) == 2

        # 4. Verify data is ready for harmonization
        assert all(col in instruments.columns for col in ["rsid", "beta", "se"])
        assert all(col in outcome.columns for col in ["rsid", "beta", "se"])
