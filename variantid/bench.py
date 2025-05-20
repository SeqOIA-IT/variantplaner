import polars
import os
import sys

from variantid import variant_id

os.environ["POLARS_THREADS"]=sys.argv[1]
os.environ["RAYON_NUM_THREADS"]=sys.argv[2]

df = polars.read_parquet("bench_data/HG001.v.parquet")
df = df.rename({"id": "old_id"})

chr2len = polars.read_csv("bench_data/grch38.92.csv",)
chr2len = chr2len.with_columns(offset=polars.col("length").cum_sum() - polars.col("length"))
chr2len = chr2len.cast({"offset": polars.UInt64})
real_pos_max = chr2len.select([polars.col("length").sum()]).get_column("length").max()

df = df.join(chr2len, right_on="contig", left_on="chr", how="left", coalesce=True)
df = df.with_columns(real_pos=polars.col("pos") + polars.col("offset"))

df = df.with_columns(
    new_id=variant_id.compute_id(
        "real_pos",
        "ref",
        "alt",
        real_pos_max,
    )
)

same = df.with_columns(val=polars.col("old_id") == polars.col("new_id")).get_column("val").all()

assert same, "id are different"
