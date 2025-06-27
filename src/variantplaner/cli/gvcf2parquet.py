"""Module contains gvcf2parquet subcommand entry point function."""

# std import
from __future__ import annotations

import logging
import pathlib
import sys

# 3rd party import
import click
import polars

# project import
from variantplaner import ContigsLength, Vcf, cli, exception, normalization


@cli.main.group("gvcf2parquet", chain=True)  # type: ignore[has-type]
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
    chr2len.from_vcf_header_and_path(vcf.header, chrom2length_path)

    local_vcf_lf = vcf.lf.filter(polars.col("alt") != "<NON_REF>").with_columns(
        alt=polars.col("alt").str.replace(",<NON_REF>", "")
    )
    local_vcf_lf = normalization.add_variant_id(vcf.lf, chr2len.lf)

    variants = local_vcf_lf

    try:
        variants.sink_parquet(output_path)
    except polars.exceptions.InvalidOperationError:
        variants.collect().write_parquet(output_path)
    except polars.exceptions.ColumnNotFoundError:
        variants.collect().write_parquet(output_path)
    logger.info(f"End write variants in {output_path}")


@gvcf2parquet.command("genotypes")
@click.pass_context
@click.option(
    "-o",
    "--output-path",
    help="Path where genotypes will be written.",
    type=click.Path(writable=True, path_type=pathlib.Path),
    required=True,
)
def genotypes(
    ctx: click.Context,
    output_path: pathlib.Path,
) -> None:
    """Write genotypes."""
    logger = logging.getLogger("vcf2parquet.genotypes")

    lf = ctx.obj["lazyframe"]
    headers_obj = lf.header

    logger.debug(f"parameter: {output_path=}")

    try:
        genotypes_data = lf.genotypes()
    except exception.NoGenotypeError:
        logger.error("It's seems vcf not contains genotypes information.")  # noqa: TRY400  we are in cli exception isn't readable
        sys.exit(14)

    schema = genotypes_data.lf.collect_schema()
    metadata = headers_obj.build_metadata([n.lower() for n in schema.names()])

    logger.info(f"Start write genotypes in {output_path}")
    try:
        genotypes_data.lf.sink_parquet(output_path, maintain_order=False, metadata=metadata)
    except polars.exceptions.InvalidOperationError:
        genotypes_data.lf.collect(engine="cpu").write_parquet(output_path, metadata=metadata)
    except polars.exceptions.ColumnNotFoundError:
        genotypes_data.lf.collect(engine="cpu").write_parquet(output_path, metadata=metadata)
    logger.info(f"End write genotypes in {output_path}")


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
    logger = logging.getLogger("gvcf2parquet.coverage")

    lf = ctx.obj["lazyframe"]

    variants = lf.variants()

    try:
        genotypes_data = lf.genotypes()
    except exception.NoGenotypeError:
        logger.error("It's seems vcf not contains genotypes information.")  # noqa: TRY400  we are in cli exception isn't readable
        sys.exit(14)

    try:
        coverages = genotypes_data.coverages(variants)
    except exception.NoDPError:
        logger.error("It's seems vcf not contains coverage information.")  # noqa: TRY400  we are in cli exception isn't readable
        sys.exit(15)
    except exception.NoGQError:
        logger.error("It's seems vcf not contains genotypes information.")  # noqa: TRY400  we are in cli exception isn't readable
        sys.exit(16)

    # coverages.fill_gap()

    logger.info(f"Start write annotations in {output_path}")
    try:
        coverages.lf.sink_parquet(output_path, maintain_order=False)
    except polars.exceptions.InvalidOperationError:
        coverages.lf.collect(engine="cpu").write_parquet(output_path)
    except polars.exceptions.ColumnNotFoundError:
        coverages.lf.collect(engine="cpu").write_parquet(output_path)
    logger.info(f"End write annotations in {output_path}")
