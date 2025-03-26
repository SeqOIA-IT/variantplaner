"""
Register Expressions extension with extra functionality.

Enables you to write

    polars.col("real_pos").variant_id.add_id(polars.col("ref"), polars.col("alt"), polars.lit(120))

However, note that:

- you will need to add `import variantid.variant_id` to your code.
  Add `# noqa: F401` to avoid linting errors due to unused imports.
- static typing will not recognise your custom namespace. Errors such
  as `"LazyFrame" has no attribute "variant_id"  [attr-defined]`.
"""

# std import
from __future__ import annotations

import typing

# 3rd party import
import polars

# project import
import variantid
import variantid.variant_id


@polars.api.register_expr_namespace("variant_id")
class VariantId:
    def __init__(self, expr: polars.Expr) -> None:
        self._expr = expr

    def __getattr__(self, attr: str) -> typing.Callable[..., polars.Expr]:
        if attr in ("compute_id", "compute_part"):

            def func(*args: typing.Any, **kwargs: typing.Any) -> polars.Expr:
                return getattr(variantid.variant_id, attr)(self._expr, *args, **kwargs)

            return func
        raise AttributeError(f"{self.__class__} has no attribute {attr}")
