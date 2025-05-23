"""Function use to normalize data."""

# std import
from __future__ import annotations

import logging

# 3rd party import
import polars

# project import
from variantid import variant_id  # type: ignore[attr-defined]

logger = logging.getLogger("normalization")


def add_variant_id(lf: polars.LazyFrame, chrom2length: polars.LazyFrame) -> polars.LazyFrame:
    """Add a column id of variants.

    Id computation is based on

    Two different algorithms are used to calculate the variant identifier, depending on the cumulative length of the reference and alternative sequences.

    If the cumulative length of the reference and alternative sequences is short, the leftmost bit of the id is set to 0, then a unique 63-bit hash of the variant is calculated.

    If the cumulative length of the reference and alternative sequences is long, the right-most bit of the id will have a value of 1, followed by a hash function, used in Firefox, of the chromosome, position, reference and alternative sequence without the right-most bit.

    If lf.columns contains SVTYPE and SVLEN variant with regex group in alt <([^:]+).*> match SVTYPE are replaced by concatenation of SVTYPE and SVLEN first value.

    Args:
        lf: [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html) contains: chr, pos, ref, alt columns.
        chrom2length: [polars.DataFrame](https://pola-rs.github.io/polars/py-polars/html/reference/dataframe/index.html) contains: chr and length columns.

    Returns:
        [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html) with chr column normalized
    """
    real_pos_max = chrom2length.select([polars.col("length").sum()]).collect().get_column("length").max()

    large_variant_len = (64 - len(format(real_pos_max, "b")) - 2) // 2 + 1

    col_names = lf.collect_schema().names()
    if "SVTYPE" in col_names and "SVLEN" in col_names:
        lf = lf.with_columns(
            alt=polars.when(
                polars.col("alt").str.replace("<(?<type>[^:]+).*>", "$type") == polars.col("SVTYPE"),
            )
            .then(
                polars.col("alt")
                .str.replace(
                    ".+",
                    polars.concat_str(
                        [polars.col("SVTYPE"), polars.col("SVLEN").list.get(0)],
                        separator="-",
                    ),
                )
                .str.pad_end(large_variant_len, "-"),
            )
            .otherwise(
                polars.col("alt"),
            ),
        )

    lf = lf.with_columns(alt=polars.col("alt").str.replace("\\*", "*" * large_variant_len))
    lf = lf.join(chrom2length, right_on="contig", left_on="chr", how="left", coalesce=True)
    lf = lf.with_columns(real_pos=polars.col("pos") + polars.col("offset"))

    lf = lf.with_columns(
        id=variant_id.compute_id(
            "real_pos",
            "ref",
            "alt",
            real_pos_max,
        ),
    )

    return lf.drop(["real_pos", "length", "offset"])


def add_id_part(lf: polars.LazyFrame, number_of_bits: int = 8) -> polars.LazyFrame:
    """Add column id part.

    If id is large variant id value, id_part are set to 255, other value most weigthed position 8 bits are use.

    Args:
        lf: [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html) contains: id column.

    Returns:
        [polars.LazyFrame](https://pola-rs.github.io/polars/py-polars/html/reference/lazyframe/index.html) with column id_part added
    """
    return lf.with_columns(id_part=variant_id.compute_part("id", number_of_bits=number_of_bits))
