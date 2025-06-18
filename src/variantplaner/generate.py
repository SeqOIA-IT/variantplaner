"""Function to generate information."""

# std import
from __future__ import annotations

import itertools
import logging

# 3rd party import
import polars

# project import
from variantplaner.exception import NoGTError

logger = logging.getLogger("generate")

gt2chr = {i: chr(i + 33) for i in range(94)}


def transmission_ped(
    genotypes_lf: polars.LazyFrame,
    pedigree_lf: polars.LazyFrame,
) -> polars.DataFrame | None:
    """Compute transmission of each variants.

    **Warning**: only the first sample with two parent are considered.

    Args:
        genotypes_lf: Genotypes [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html), `gt` column are required.
        pedigree_lf: Pedigree [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html).

    Returns:
         DataFrame with transmission information

    Raises:
        NoGTError: If genotypes_lf not contains gt column.
    """
    pedigree_df = pedigree_lf.collect()

    pedigree_df = pedigree_df.filter(polars.col("father_id").is_not_null() | polars.col("mother_id").is_not_null())

    return transmission(
        genotypes_lf,
        tuple(pedigree_df.get_column("personal_id").to_list()),
        tuple(pedigree_df.get_column("mother_id").to_list()),
        tuple(pedigree_df.get_column("father_id").to_list()),
    )


def transmission(
    genotypes_lf: polars.LazyFrame,
    index_names: tuple[str],
    mother_names: tuple[str | None] = (None,),
    father_names: tuple[str | None] = (None,),
) -> polars.DataFrame | None:
    """Compute how each variant are transmite to index case.

    Args:
        genotypes_lf: Genotypes [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html), `gt` column are required.
        index_name: Sample name of index case.
        mother_name: Sample name of mother.
        father_name: Sample name of father.

    Returns:
         [polars.DataFrame](https://pola-rs.github.io/polars/py-polars/html/reference/dataframe/index.html) with transmission information. With genotyping information for index, mother and father. If any of them isn't present value are set to polars.Null. Columns transmission contains a string: concat(chr(index_gt + 33), chr(mother_gt + 33), chr(father_gt + 33)), transmission: `#~!` mean homozygote diploide variant not present in father but with no information about mother.

    Raises:
        NoGTError: if genotypes_lf not containts gt column.
    """
    genotypes_column = list(genotypes_lf.collect_schema().names()[2:])
    if "gt" not in genotypes_column:
        raise NoGTError("genotype polars.LazyFrame")

    genotypes_df = genotypes_lf.collect()

    dfs = []
    for names in itertools.zip_longest(index_names, mother_names, father_names, fillvalue=None):
        df = __trio(genotypes_df, genotypes_column, *names)
        if df is not None:
            dfs.append(df)

    if len(dfs) > 0:
        return polars.concat(dfs)
    return None


def __trio(
    genotypes_df: polars.DataFrame,
    genotypes_column: list[str],
    index_name: str | None = None,
    mother_name: str | None = None,
    father_name: str | None = None,
) -> polars.DataFrame | None:
    """Compute transmission of one trio."""
    if index_name is None:
        return None

    index_df = genotypes_df.filter(polars.col("sample") == index_name).rename(
        {colname: f"index_{colname}" for colname in genotypes_column}
    )

    if mother_name is None:
        mother_df = polars.DataFrame(schema=genotypes_df.schema)
    else:
        mother_df = genotypes_df.filter(polars.col("sample") == mother_name)
    mother_df = mother_df.rename({colname: f"mother_{colname}" for colname in genotypes_column}).drop("sample")

    if father_name is None:
        father_df = polars.DataFrame(schema=genotypes_df.schema)
    else:
        father_df = genotypes_df.filter(polars.col("sample") == father_name)
    father_df = father_df.rename({colname: f"father_{colname}" for colname in genotypes_column}).drop("sample")

    parent_df = mother_df.join(father_df, on="id", how="full", coalesce=True)
    transmission_df = index_df.join(parent_df, on="id", how="left")

    if father_name is not None:
        transmission_df = transmission_df.with_columns(father_gt=polars.col("father_gt").fill_null(strategy="zero"))
    if mother_name is not None:
        transmission_df = transmission_df.with_columns(mother_gt=polars.col("mother_gt").fill_null(strategy="zero"))

    return transmission_df.with_columns(
        polars.concat_str(
            polars.col("index_gt").replace_strict(gt2chr, default="~", return_dtype=polars.Utf8),
            polars.col("mother_gt").fill_null(94).replace_strict(gt2chr, default="~", return_dtype=polars.Utf8),
            polars.col("father_gt").fill_null(94).replace_strict(gt2chr, default="~", return_dtype=polars.Utf8),
        ).alias("origin"),
    )
