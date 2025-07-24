"""Tests for the `io.vcf` module."""

# std import
from __future__ import annotations

import os
import pathlib
import typing

# 3rd party import
import polars

try:
    from pytest_cov.embed import cleanup_on_sigterm
except ImportError:  # pragma: no cover
    pass
else:
    cleanup_on_sigterm()


# project import
from variantplaner import struct

DATA_DIR = pathlib.Path(__file__).parent / "data"


def __scantree(path: pathlib.Path) -> typing.Iterator[pathlib.Path]:
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from __scantree(pathlib.Path(entry.path))
        else:
            yield pathlib.Path(entry.path)


def test_hive(tmp_path: pathlib.Path) -> None:
    """Check partition genotype parquet."""
    struct.genotypes.hive(
        [
            DATA_DIR / "one.g.parquet",
            DATA_DIR / "two.g.parquet",
        ],
        tmp_path,
        2,
        1,
        append=False,
    )

    partition_paths = set(__scantree(tmp_path))

    value = polars.concat([polars.read_parquet(path, hive_partitioning=False) for path in partition_paths]).drop(
        "id_part"
    )
    truth = polars.concat(
        [
            polars.read_parquet(DATA_DIR / "one.g.parquet"),
            polars.read_parquet(DATA_DIR / "two.g.parquet"),
        ],
    )

    assert sorted(value.get_column("id").to_list()) == sorted(truth.get_column("id").to_list())
    assert sorted(value.get_column("sample").to_list()) == sorted(truth.get_column("sample").to_list())
    assert sorted(value.get_column("gt").to_list()) == sorted(truth.get_column("gt").to_list())
    assert sorted(value.get_column("ad").to_list()) == sorted(truth.get_column("ad").to_list())
    assert sorted(value.get_column("dp").to_list()) == sorted(truth.get_column("dp").to_list())
    assert sorted(value.get_column("gq").fill_null(0).to_list()) == sorted(
        truth.get_column("gq").fill_null(0).to_list(),
    )


def test_hive_512_part(tmp_path: pathlib.Path) -> None:
    """Check partition genotype parquet."""
    struct.genotypes.hive(
        [
            DATA_DIR / "one.g.parquet",
            DATA_DIR / "two.g.parquet",
        ],
        tmp_path,
        2,
        1,
        append=False,
        number_of_bits=9,
    )

    partition_paths = set(__scantree(tmp_path))

    value = polars.concat([polars.read_parquet(path, hive_partitioning=False) for path in partition_paths]).drop(
        "id_part"
    )
    truth = polars.concat(
        [
            polars.read_parquet(DATA_DIR / "one.g.parquet"),
            polars.read_parquet(DATA_DIR / "two.g.parquet"),
        ],
    )

    assert sorted(value.get_column("id").to_list()) == sorted(truth.get_column("id").to_list())
    assert sorted(value.get_column("sample").to_list()) == sorted(truth.get_column("sample").to_list())
    assert sorted(value.get_column("gt").to_list()) == sorted(truth.get_column("gt").to_list())
    assert sorted(value.get_column("ad").to_list()) == sorted(truth.get_column("ad").to_list())
    assert sorted(value.get_column("dp").to_list()) == sorted(truth.get_column("dp").to_list())
    assert sorted(value.get_column("gq").fill_null(0).to_list()) == sorted(
        truth.get_column("gq").fill_null(0).to_list(),
    )


def test_hive_append(tmp_path: pathlib.Path) -> None:
    """Check partition genotype parquet."""
    struct.genotypes.hive(
        [
            DATA_DIR / "one.g.parquet",
            DATA_DIR / "two.g.parquet",
        ],
        tmp_path,
        2,
        1,
        append=False,
    )

    struct.genotypes.hive(
        [
            DATA_DIR / "three.g.parquet",
        ],
        tmp_path,
        2,
        1,
        append=True,
    )

    partition_paths = set(__scantree(tmp_path))

    value = polars.concat([polars.read_parquet(path, hive_partitioning=False) for path in partition_paths])
    truth = polars.concat(
        [
            polars.read_parquet(DATA_DIR / "one.g.parquet"),
            polars.read_parquet(DATA_DIR / "two.g.parquet"),
            polars.read_parquet(DATA_DIR / "three.g.parquet"),
        ],
    )

    assert sorted(value.get_column("id").to_list()) == sorted(truth.get_column("id").to_list())
    assert sorted(value.get_column("sample").to_list()) == sorted(truth.get_column("sample").to_list())
    assert sorted(value.get_column("gt").to_list()) == sorted(truth.get_column("gt").to_list())
    assert sorted(value.get_column("ad").to_list()) == sorted(truth.get_column("ad").to_list())
    assert sorted(value.get_column("dp").to_list()) == sorted(truth.get_column("dp").to_list())
    assert sorted(value.get_column("gq").fill_null(0).to_list()) == sorted(
        truth.get_column("gq").fill_null(0).to_list(),
    )


def test_hive_column_order(tmp_path: pathlib.Path) -> None:
    """Check partition genotype parquet."""
    tmp_path_one = tmp_path / "one_reorder.g.parget"
    tmp_path_two = tmp_path / "two_reorder.g.parget"

    df = polars.read_parquet(DATA_DIR / "one.g.parquet")
    column_order = sorted(df.schema.names())
    df = df.select(column_order)
    df.write_parquet(tmp_path_one)

    df = polars.read_parquet(DATA_DIR / "two.g.parquet")
    column_order.reverse()
    df = df.select(column_order)
    df.write_parquet(tmp_path_two)

    struct.genotypes.hive(
        [
            tmp_path_one,
            tmp_path_two,
        ],
        tmp_path / "partitions",
        2,
        1,
        append=False,
    )

    partition_paths = set(__scantree(tmp_path / "partitions"))

    value = polars.concat([polars.read_parquet(path, hive_partitioning=False).select(column_order) for path in partition_paths])

    truth = polars.concat(
        [
            polars.read_parquet(DATA_DIR / "one.g.parquet"),
            polars.read_parquet(DATA_DIR / "two.g.parquet"),
        ],
    )

    truth = truth.select(column_order)

    value = value.sort(by="id")
    truth = truth.sort(by="id")

    polars.testing.assert_frame_equal(value, truth, check_row_order=False, check_column_order=False)
