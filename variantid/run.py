import polars

from variantid import variant_id

df = polars.DataFrame(
    data={
        "real_pos": list(range(10, 110, 10)),
        "ref": ["A", "C", "T", "G", "A", "C", "T", "G", "A", "C"],
        "alt": ["T", "G", "A", "C", "T", "G", "A", "C", "T", "G"],
    },
    schema={
        "real_pos": polars.UInt64,
        "ref": polars.Utf8,
        "alt": polars.Utf8,
    },
)

lf = df.lazy()

lf = lf.with_columns(
    id = variant_id.compute_id(
        "real_pos",
        "ref",
        "alt",
        120
    )
)

lf = lf.with_columns(
    part = variant_id.compute_part("id", number_of_bits=8)
)

print(lf.collect())

lf = lf.with_columns(
    part = variant_id.compute_part("id", number_of_bits=9)
)

print(lf.collect())
