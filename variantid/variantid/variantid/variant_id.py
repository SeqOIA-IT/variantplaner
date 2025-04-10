# std import

# 3rd party import
import polars

# project import
import variantid
import variantid._utils
import variantid._typing


def compute_id(
    pos: variantid._typing.IntoExprColumn,
    ref: variantid._typing.IntoExprColumn,
    alt: variantid._typing.IntoExprColumn,
    max_pos: int,
) -> polars.Expr:
    return polars.plugins.register_plugin_function(
        plugin_path=variantid._utils.LIB,
        args=[pos, ref, alt],
        kwargs={"max_pos": max_pos},
        function_name="compute_id",
    )


def compute_part(
    id: variantid._typing.IntoExprColumn,
    number_of_bits: int,
) -> polars.Expr:
    print("LIB PATH", variantid._utils.LIB)
    return polars.plugins.register_plugin_function(
        plugin_path=variantid._utils.LIB,
        args=[id],
        kwargs={
            "number_of_bits": number_of_bits,
        },
        function_name="compute_part",
    )
