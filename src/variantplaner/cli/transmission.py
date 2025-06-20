"""Module contains transmission subcommand entry point function."""

# std import
from __future__ import annotations

import logging
import pathlib
import sys

# 3rd party import
import click
import polars

# project import
from variantplaner import Pedigree, cli, generate


@cli.main.command("transmission")  # type: ignore[has-type]
@click.option(
    "-g",
    "--genotypes-path",
    help="Path to genotypes parquet.",
    type=click.Path(exists=True, readable=True, allow_dash=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "-p",
    "--pedigree-path",
    help="Path to pedigree file.",
    type=click.Path(exists=True, readable=True, path_type=pathlib.Path),
)
@click.option(
    "-i",
    "--index",
    help="Sample name of index.",
    type=str,
    multiple=True,
)
@click.option(
    "-m",
    "--mother",
    help="Sample name of mother.",
    type=str,
    multiple=True,
)
@click.option(
    "-f",
    "--father",
    help="Sample name of father.",
    type=str,
    multiple=True,
)
@click.option(
    "-o",
    "--output-path",
    help="Path where transmission will be write.",
    type=click.Path(writable=True, path_type=pathlib.Path),
)
def transmission(
    genotypes_path: pathlib.Path,
    output_path: pathlib.Path,
    pedigree_path: pathlib.Path | None,
    index: tuple[str] | None,
    mother: tuple[str] | None,
    father: tuple[str] | None,
) -> None:
    """Generate transmission of a genotype set."""
    logger = logging.getLogger("vcf2parquet.genotypes")

    logger.debug(f"parameter: {genotypes_path=} {output_path=} {pedigree_path=} {index=} {mother=} {father=}")

    genotypes_lf = polars.scan_parquet(genotypes_path)

    if pedigree_path:
        pedigree = Pedigree()
        pedigree.from_path(pedigree_path)
        transmission_lf: polars.DataFrame | None = generate.transmission_ped(genotypes_lf, pedigree.lf)
    elif index:
        transmission_lf = generate.transmission(
            genotypes_lf, index, mother if mother is not None else (None,), father if father is not None else (None,)
        )
    else:
        logging.error("You must specify ped file or index almost sample name")
        sys.exit(31)

    if transmission_lf is None:
        output_path.touch()
    else:
        transmission_lf.write_parquet(output_path)
