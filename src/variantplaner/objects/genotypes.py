"""Declare Genotypes object."""

# std import
from __future__ import annotations

import typing

# 3rd party import
import polars

# project import
from variantplaner.exception import (
    NoDPError,
    NoGQError,
)
from variantplaner.objects.coverages import Coverages

if typing.TYPE_CHECKING:
    from variantplaner.objects.variants import Variants


class Genotypes(polars.LazyFrame):
    """Object to manage lazyframe as Genotypes."""

    def __init__(self, data: polars.LazyFrame | None = None):
        """Initialize a Genotypes object."""
        if data is None:
            self.lf = polars.LazyFrame(schema=Genotypes.minimal_schema())
        else:
            self.lf = data

    def samples_names(self) -> list[str]:
        """Get list of sample name."""
        return self.lf.select("sample").unique("sample").collect().get_column("sample").to_list()

    def coverages(self, variants: Variants) -> Coverages:
        """Use genotypes information to compute coverages."""
        schema = self.lf.collect_schema()

        if "dp" not in schema.names():
            raise NoDPError

        if "gq" not in schema.names():
            raise NoGQError

        samples = self.lf.select("sample").unique().collect().get_column("sample")

        sublfs = []
        for sample in samples.to_list():
            sublf = self.lf.filter(polars.col("sample") == sample)

            merge = sublf.join(variants.lf, on="id")
            merge = merge.with_columns(
                end=polars.col("pos") + 1,
                coverage_min=polars.col("dp"),
                coverage_max=polars.col("dp"),
                coverage_mean=polars.col("dp"),
                coverage_median=polars.col("dp"),
                quality_min=polars.col("gq"),
                quality_max=polars.col("gq"),
                quality_mean=polars.col("gq"),
                quality_median=polars.col("gq"),
            ).rename({"pos": "start"})

            merge = merge.select(Coverages.minimal_schema().keys())

            sublfs.append(merge)

        lf = polars.concat(sublfs)

        return Coverages(lf)

    @classmethod
    def minimal_schema(cls) -> dict[str, type]:
        """Get minimal schema of genotypes polars.LazyFrame."""
        return {
            "id": polars.UInt64,
            "sample": polars.String,
        }
