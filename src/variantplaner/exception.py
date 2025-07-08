"""Exception could be generate by VariantPlanner."""

# std import
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:  # pragma: no cover
    import pathlib

# 3rd party import

# project import


class NoContigsLengthInformationError(Exception):
    """Exception raise if we didn't get Contigs Length information in vcf or in compagnion file."""

    def __init__(self):
        """Initize no contigs length information error."""
        super().__init__("Contigs length information is required in vcf header of in compagnion file.")


class NotAVariantCsvError(Exception):
    """Exception raise if file is a csv should contains variants info but columns name not match minimal requirement."""

    def __init__(self, path: pathlib.Path):
        """Initialize not a variant csv error."""
        super().__init__(f"{path} seems not be a csv variant.")


class NotVcfHeaderError(Exception):
    """Exception raise if header isn't compatible with vcf."""

    def __init__(self):
        """Initialize not a vcf header error."""
        super().__init__("Not a vcf header")


class NotAVCFError(Exception):
    """Exception raise if file read seems not be a vcf, generally not contains a line starts with '#CHROM'."""

    def __init__(self, path: pathlib.Path):
        """Initialize not a vcf error."""
        super().__init__(f"File {path} seems not be a valid vcf file.")


class NoGenotypeError(Exception):
    """Exception raise if vcf file seems not contains genotypes information."""

    def __init__(self):
        """Initialize no genotype error."""
        super().__init__("LazyFrame seems not contains genotypes.")


class NoGTError(Exception):
    """Exception raise if genotype polars.LazyFrame not contains gt column."""

    def __init__(self, message: str):
        """Initialize no gt error."""
        super().__init__(f"In {message} gt column is missing.")


class NoDPError(Exception):
    """Exception raise if genotype polars.LazyFrame not contains dp column."""

    def __init__(self):
        """Initialize no dp error."""
        super().__init__("LazyFrame seems not contains deepth coverage information.")


class NoGQError(Exception):
    """Exception raise if genotype polars.LazyFrame not contains gq column."""

    def __init__(self):
        """Initialize no gq error."""
        super().__init__("LazyFrame seems not contains quality information.")
