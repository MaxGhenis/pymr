"""PyMR: Mendelian Randomization in Python.

A modern, test-driven Python package for Mendelian Randomization analysis.

Example:
    >>> from pymr import MR, load_gwas
    >>> exposure = load_gwas("bmi_gwas.tsv.gz")
    >>> outcome = load_gwas("diabetes_gwas.tsv.gz")
    >>> mr = MR(exposure, outcome)
    >>> results = mr.run()
"""

from pymr.mr import MR
from pymr.io import load_gwas
from pymr.harmonize import harmonize

__version__ = "0.1.0"
__all__ = ["MR", "load_gwas", "harmonize"]
