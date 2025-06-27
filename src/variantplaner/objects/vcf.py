"""Declare Vcf object."""

# std import
from __future__ import annotations

import enum
import logging
import typing

# 3rd party import
import polars
import xopen

# project import
from variantplaner import normalization
from variantplaner.exception import (
    NoGenotypeError,
    NotAVCFError,
    NotVcfHeaderError,
)
from variantplaner.objects.contigs_length import ContigsLength
from variantplaner.objects.genotypes import Genotypes
from variantplaner.objects.variants import Variants
from variantplaner.objects.vcf_header import VcfHeader

# type checking block
if typing.TYPE_CHECKING:  # pragma: no cover
    import collections
    import pathlib

    from variantplaner import Annotations

logger = logging.getLogger("objects.vcf")


class VcfParsingBehavior(enum.IntFlag):
    """Enumeration use to control behavior of IntoLazyFrame."""

    NOTHING = enum.auto()
    """into_lazyframe not have any specific behavior"""

    MANAGE_SV = enum.auto()
    """into_lazyframe try to avoid structural variant id collision, SVTYPE/SVLEN info value must be present."""

    KEEP_STAR = enum.auto()
    """Keep star variant."""


class Vcf:
    """Object to manage lazyframe as Vcf."""

    def __init__(self):
        """Initialize a Vcf object."""
        self.lf = polars.LazyFrame(schema=Variants.minimal_schema())

        self.header = VcfHeader()
        self.chr2len = ContigsLength()

    def from_path(
        self,
        path: pathlib.Path,
        chr2len_path: pathlib.Path | None,
        behavior: VcfParsingBehavior = VcfParsingBehavior.NOTHING,
    ) -> None:
        """Populate Vcf object with vcf file."""
        with xopen.xopen(path) as fh:
            try:
                self.header.from_lines(fh)
            except NotVcfHeaderError as e:
                raise NotAVCFError(path) from e

        self.chr2len.from_vcf_header_and_path(self.header, chr2len_path)

        self.lf = polars.scan_csv(
            path,
            separator="\t",
            comment_prefix="#",
            has_header=False,
            schema_overrides=Vcf.schema(),
            new_columns=list(Vcf.schema().keys()),
        )

        schema = self.lf.collect_schema()
        self.lf = self.lf.rename(dict(zip(schema.names(), self.header.column_name(schema.len()))))
        self.lf = self.lf.cast(Vcf.schema())

        if behavior & VcfParsingBehavior.MANAGE_SV:
            self.lf = self.lf.with_columns(self.header.info_parser({"SVTYPE", "SVLEN"}))

        if behavior & VcfParsingBehavior.KEEP_STAR:
            self.lf = self.lf.filter(polars.col("alt") != "*")

        self.lf = normalization.add_variant_id(self.lf, self.chr2len.lf)

        if behavior & VcfParsingBehavior.MANAGE_SV:
            self.lf = self.lf.drop("SVTYPE", "SVLEN", strict=False)

    def variants(self) -> Variants:
        """Get variants of vcf."""
        return Variants(self.lf.select(Variants.minimal_schema().keys()))

    def set_variants(self, variants: Variants) -> None:
        """Set variants of vcf."""
        self.lf = variants.lf

    def genotypes(self) -> Genotypes:
        """Get genotype of vcf."""
        schema = self.lf.collect_schema()

        if "format" not in schema.names():
            raise NoGenotypeError

        lf = self.lf.select([*schema.names()[schema.names().index("format") :]])
        schema = lf.collect_schema()

        # Split genotype column in sub value
        col2expr = self.header.format_parser()

        format_strs = lf.select("format").unique().collect().get_column("format")

        sublfs = []
        for fstr in format_strs.to_list():
            # Found index of genotyping value
            col_index = {
                key: index
                for (index, key) in enumerate(
                    fstr.split(":"),
                )
            }

            sublf = lf.filter(polars.col("format") == fstr)

            # Pivot value
            sublf = sublf.unpivot(index=["id"]).with_columns(
                [
                    polars.col("id"),
                    polars.col("variable").alias("sample"),
                    polars.col("value").str.split(":"),
                ],
            )

            conversion = []
            for col in col2expr:
                if col in col_index:
                    conversion.append(
                        polars.col("value")
                        .list.get(col_index[col], null_on_oob=True)
                        .pipe(function=col2expr[col], col_name=col)
                    )
                else:
                    conversion.append(polars.lit("").pipe(function=col2expr[col], col_name=col))

            sublf = sublf.with_columns(conversion)

            sublfs.append(sublf)

        lf = polars.concat(sublfs).drop("variable", "value")

        if "gt".upper() in col2expr:
            lf = lf.filter(polars.col("gt") != 0)

        return Genotypes(lf)

    def add_genotypes(self, genotypes_lf: Genotypes) -> None:
        """Add genotypes information in vcf."""
        for sample in genotypes_lf.samples_names():
            geno2sample = (
                genotypes_lf.lf.filter(polars.col("sample") == sample)
                .rename(
                    {col: f"{sample}_{col}" for col in genotypes_lf.lf.collect_schema().names()[2:]},
                )
                .drop("sample")
            )
            self.lf = self.lf.join(geno2sample, on="id", how="full", coalesce=True)

    def annotations(self, select_info: set[str] | None = None) -> Annotations:
        """Get annotations of vcf."""
        lf = self.lf.with_columns(self.lf.header.info_parser(select_info))

        return lf.drop("chr", "pos", "ref", "alt", "format", "info")

    @classmethod
    def schema(cls) -> collections.abc.Mapping[str, polars._typing.PolarsDataType]:
        """Get schema of Vcf polars.LazyFrame."""
        return {
            "chr": polars.String,
            "pos": polars.UInt64,
            "vid": polars.String,
            "ref": polars.String,
            "alt": polars.String,
            "qual": polars.String,
            "filter": polars.String,
            "info": polars.String,
        }
