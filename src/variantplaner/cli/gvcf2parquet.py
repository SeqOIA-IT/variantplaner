"""Module contains gvcf2parquet subcommand entry point function."""

# std import
from __future__ import annotations

import logging
import pathlib

# 3rd party import
import click
import polars

# project import
from variantplaner import Vcf, cli


@cli.main.group("gvcf2parquet", chain=True)
@click.pass_context
@click.option(
    "-i",
    "--input-path",
    help="Path to gvcf input file.",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        allow_dash=True,
        path_type=pathlib.Path,
    ),
    required=True,
)
@click.option(
    "-c",
    "--chrom2length-path",
    help="CSV file that associates a chromosome name with its size.",
    type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path),
)
def gvcf2parquet(
    ctx: click.Context,
    input_path: pathlib.Path,
    chrom2length_path: pathlib.Path | None,
) -> None:
    """Convert a gvcf in parquet."""
    logger = logging.getLogger("gvc2parquet")

    logger.debug(f"parmeter: {input_path=} {chrom2length_path=}")

    lf = Vcf()

    logger.debug("Start read vcf")
    lf.from_path(input_path, chrom2length_path)
    logger.debug("End read vcf")

    ctx.obj["lazyframe"] = lf
    ctx.obj["chrom2length_path"] = chrom2length_path


@gvcf2parquet.command("variants")
@click.pass_context
@click.option(
    "-o",
    "--output-path",
    help="Path where variants will be written.",
    type=click.Path(writable=True, path_type=pathlib.Path),
    required=True,
)
def variants(
    ctx: click.Context,
    output_path: pathlib.Path,
) -> None:
    """Write variants."""
    logger = logging.getLogger("vcf2parquet.variants")

    vcf = ctx.obj["lazyframe"]
    chrom2length_path = ctx.obj["chrom2length_path"]


    logger.info(f"parameter: {output_path=}")

    chr2len = ContigsLength()
    if chr2len_path is not None:
        if chr2len.from_path(chr2len_path) == 0 and chr2len.from_vcf_header(self.header) == 0:
            raise NoContigsLengthInformationError
        elif chr2len.from_vcf_header(self.header) == 0:
            raise NoContigsLengthInformationError



    vcf.lf = (
        vcf.lf
        .filter(polars.col("alt")!="<NON_REF>")
        .with_columns(
            alt = polars.col("alt").str.replace(",<NON_REF>", "")
        )
    )
    vcf.lf = normalization.add_variant_id(vcf.lf, chr2len.lf)
    print(vcf.lf.select("id", "chr", "pos", "ref", "alt").collect())

    variants = vcf.variants()

    try:
        variants.lf.sink_parquet(output_path)
    except polars.exceptions.InvalidOperationError:
        variants.lf.collect().write_parquet(output_path)
    except polars.exceptions.ColumnNotFoundError:
        variants.lf.collect().write_parquet(output_path)
    logger.info(f"End write variants in {output_path}")


@gvcf2parquet.command("coverage")
@click.pass_context
@click.option(
    "-o",
    "--output-path",
    help="Path where coverage will be written.",
    type=click.Path(writable=True, path_type=pathlib.Path),
    required=True,
)
def coverage(
    ctx: click.Context,
    output_path: pathlib.Path,
) -> None:
    """Write coverage."""
    logger = logging.getLogger("vcf2parquet.coverage")

    _lf = ctx.obj["lazyframe"]

    logger.debug(f"parameter: {output_path=}")
