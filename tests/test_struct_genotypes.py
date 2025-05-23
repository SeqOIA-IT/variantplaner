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
