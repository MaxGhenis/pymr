"""IEU OpenGWAS API integration for PyMR.

This module provides access to the IEU OpenGWAS database API for:
- Fetching genetic instruments (top hits with clumping)
- Looking up SNPs in outcome GWAS datasets
- Searching and listing available GWAS studies

References:
    API Documentation: https://gwas-api.mrcieu.ac.uk/
    ieugwasr R package: https://mrcieu.github.io/ieugwasr/
"""

import os
from typing import Any, Optional

import pandas as pd
import requests


class IEUClient:
    """Client for accessing the IEU OpenGWAS API.

    Args:
        base_url: Base URL for the API (default: https://gwas-api.mrcieu.ac.uk)
        jwt: JSON Web Token for authentication. If not provided, reads from
            OPENGWAS_JWT environment variable.

    Example:
        >>> client = IEUClient(jwt="your_token_here")
        >>> instruments = client.get_tophits("ieu-a-2")
    """

    def __init__(
        self,
        base_url: str = "https://gwas-api.mrcieu.ac.uk",
        jwt: Optional[str] = None,
    ) -> None:
        """Initialize the IEU OpenGWAS API client."""
        self.base_url = base_url
        self.jwt = jwt or os.environ.get("OPENGWAS_JWT")

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary of headers including authentication if JWT is available.
        """
        headers = {"Content-Type": "application/json"}
        if self.jwt:
            headers["Authorization"] = f"Bearer {self.jwt}"
        return headers

    def get_tophits(
        self,
        gwas_id: str,
        pval: float = 5e-8,
        clump: bool = True,
        r2: float = 0.001,
        kb: int = 10000,
    ) -> list[dict[str, Any]]:
        """Fetch top hits (genetic instruments) from a GWAS dataset.

        Args:
            gwas_id: GWAS dataset identifier (e.g., "ieu-a-2")
            pval: P-value threshold for significance (default: 5e-8)
            clump: Whether to perform LD clumping (default: True)
            r2: LD clumping r² threshold (default: 0.001)
            kb: LD clumping distance in kb (default: 10000)

        Returns:
            List of dictionaries containing variant information.
        """
        url = f"{self.base_url}/tophits/{gwas_id}"
        params = {
            "pval": pval,
            "clump": 1 if clump else 0,
            "r2": r2,
            "kb": kb,
        }
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_associations(
        self,
        gwas_id: str,
        variants: list[str],
        proxies: bool = False,
    ) -> list[dict[str, Any]]:
        """Look up specific variants in a GWAS dataset.

        Args:
            gwas_id: GWAS dataset identifier (e.g., "ieu-a-7")
            variants: List of variant identifiers (rsIDs)
            proxies: Whether to use LD proxies for missing variants (default: False)

        Returns:
            List of dictionaries containing association statistics.
        """
        url = f"{self.base_url}/associations/{gwas_id}"
        data = {
            "variant": variants,
            "proxies": 1 if proxies else 0,
        }
        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_gwasinfo(self, query: Optional[str] = None) -> list[dict[str, Any]]:
        """Get information about available GWAS datasets.

        Args:
            query: Optional search query to filter datasets

        Returns:
            List of dictionaries containing GWAS metadata.
        """
        url = f"{self.base_url}/gwasinfo"
        params = {}
        if query:
            params["trait"] = query
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


def get_instruments(
    exposure_id: str,
    p_threshold: float = 5e-8,
    clump: bool = True,
    r2: float = 0.001,
    kb: int = 10000,
    jwt: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch genetic instruments (clumped top hits) for an exposure.

    This is a convenience function that wraps IEUClient.get_tophits().

    Args:
        exposure_id: GWAS dataset identifier for exposure (e.g., "ieu-a-2")
        p_threshold: P-value threshold for significance (default: 5e-8)
        clump: Whether to perform LD clumping (default: True)
        r2: LD clumping r² threshold (default: 0.001)
        kb: LD clumping distance in kb (default: 10000)
        jwt: Optional JWT token for authentication

    Returns:
        DataFrame with columns: rsid, chr, position, ea, nea, beta, se, pval, eaf

    Example:
        >>> instruments = get_instruments("ieu-a-2")  # BMI GWAS
        >>> print(instruments.head())
    """
    client = IEUClient(jwt=jwt)
    results = client.get_tophits(
        gwas_id=exposure_id,
        pval=p_threshold,
        clump=clump,
        r2=r2,
        kb=kb,
    )
    return pd.DataFrame(results)


def get_outcome(
    outcome_id: str,
    snps: list[str],
    proxies: bool = False,
    jwt: Optional[str] = None,
) -> pd.DataFrame:
    """Look up SNPs in an outcome GWAS dataset.

    This is a convenience function that wraps IEUClient.get_associations().

    Args:
        outcome_id: GWAS dataset identifier for outcome (e.g., "ieu-a-7")
        snps: List of SNP rsIDs to look up
        proxies: Whether to use LD proxies for missing SNPs (default: False)
        jwt: Optional JWT token for authentication

    Returns:
        DataFrame with association statistics for the requested SNPs

    Example:
        >>> outcome = get_outcome("ieu-a-7", ["rs123", "rs456"])
        >>> print(outcome[["rsid", "beta", "pval"]])
    """
    client = IEUClient(jwt=jwt)
    results = client.get_associations(
        gwas_id=outcome_id,
        variants=snps,
        proxies=proxies,
    )
    return pd.DataFrame(results)


def search_gwas(query: str, jwt: Optional[str] = None) -> pd.DataFrame:
    """Search for GWAS datasets by keyword.

    Args:
        query: Search query (e.g., "body mass index")
        jwt: Optional JWT token for authentication

    Returns:
        DataFrame with matching GWAS datasets

    Example:
        >>> results = search_gwas("diabetes")
        >>> print(results[["id", "trait", "sample_size"]])
    """
    client = IEUClient(jwt=jwt)
    results = client.get_gwasinfo(query=query)
    return pd.DataFrame(results)


def list_gwas(jwt: Optional[str] = None) -> pd.DataFrame:
    """List all available GWAS datasets.

    Args:
        jwt: Optional JWT token for authentication

    Returns:
        DataFrame with all available GWAS datasets

    Example:
        >>> all_gwas = list_gwas()
        >>> print(f"Total datasets: {len(all_gwas)}")
    """
    client = IEUClient(jwt=jwt)
    results = client.get_gwasinfo()
    return pd.DataFrame(results)
