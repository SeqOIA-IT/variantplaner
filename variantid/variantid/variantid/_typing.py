# std import
import typing
import sys

# 3rd project import
import polars

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

IntoExprColumn: TypeAlias = typing.Union[polars.Expr, str, polars.Series]
