"""VariantPlaner, a tool kit to manage many variants without many cpu and ram resource.

Convert a vcf in parquet, convert annotations in parquet, convert parquet in vcf.

But also build a file struct to get a fast variant database interrogations time.
"""

from __future__ import annotations

import typing
import uuid

from variantplaner import generate, normalization, struct
from variantplaner.objects import (
    Annotations,
    ContigsLength,
    Genotypes,
    Pedigree,
    Variants,
    Vcf,
    VcfHeader,
    VcfParsingBehavior,
)


def any2string(value: typing.Any) -> str:
    """Convert an int in a string. Use for temp file creation."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, str(value)))


__all__: list[str] = [
    "Annotations",
    "ContigsLength",
    "Genotypes",
    "Pedigree",
    "Variants",
    "Vcf",
    "VcfHeader",
    "VcfParsingBehavior",
    "exception",
    "generate",
    "io",
    "normalization",
    "struct",
]
__version__: str = "0.5.0"
