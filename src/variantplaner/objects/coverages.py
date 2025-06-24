"""Declare Coverages object."""

# std import
from __future__ import annotations

# 3rd party import
import polars

# project import


SIZE_OF_GAP_GROUP = 2


class Coverages(polars.LazyFrame):
    """Object to manage lazyframe as Coverages."""

    def __init__(self, data: polars.LazyFrame | None = None):
        """Initialize a Coverages object."""
        if data is None:
            self.lf = polars.LazyFrame(schema=Coverages.minimal_schema())
        else:
            self.lf = data

    def fill_gap(self) -> None:
        """Compute gap between variants."""
        gap = (
            self.lf.with_row_index()
            .cast(
                {
                    "index": polars.Int64,
                }
            )
            .group_by_dynamic("index", every="2i", group_by=["chr", "sample"])
            .agg(
                start=polars.col("end").min(),
                end=polars.col("start").max(),
                coverage_min=polars.col("coverage_min").min(),
                coverage_max=polars.col("coverage_max").max(),
                coverage_mean=polars.col("coverage_mean").mean(),
                coverage_median=polars.col("coverage_median").mean(),
                quality_min=polars.col("quality_min").min(),
                quality_max=polars.col("quality_max").max(),
                quality_mean=polars.col("quality_mean").mean(),
                quality_median=polars.col("quality_median").mean(),
                types=polars.lit("gap"),
                n=polars.len(),
            )
            .filter(polars.col("n") == SIZE_OF_GAP_GROUP)
            .cast(
                {
                    "start": polars.UInt64,
                    "end": polars.UInt64,
                    "coverage_mean": polars.UInt32,
                    "coverage_median": polars.UInt32,
                    "quality_mean": polars.UInt32,
                    "quality_median": polars.UInt32,
                }
            )
            .collect()
        )

        gap = gap.select(
            [
                "chr",
                "start",
                "end",
                "sample",
                "coverage_min",
                "coverage_max",
                "coverage_mean",
                "coverage_median",
                "quality_min",
                "quality_max",
                "quality_mean",
                "quality_median",
                "types",
            ]
        )
        self.lf = self.lf.with_columns(types=polars.lit("variant"))

        self.lf = polars.concat([gap.lazy(), self.lf]).sort("chr", "start", "end")

    @classmethod
    def minimal_schema(cls) -> dict[str, type]:
        """Get minimal schema of genotypes polars.LazyFrame."""
        return {
            "chr": polars.String,
            "start": polars.UInt64,
            "end": polars.UInt64,
            "sample": polars.String,
            "coverage_min": polars.UInt32,
            "coverage_max": polars.UInt32,
            "coverage_mean": polars.Float32,
            "coverage_median": polars.UInt32,
            "quality_min": polars.UInt32,
            "quality_max": polars.UInt32,
            "quality_mean": polars.Float32,
            "quality_median": polars.UInt32,
        }
