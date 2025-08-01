"""Development tasks."""

from __future__ import annotations

import os
import re
import sys
from contextlib import contextmanager
from importlib.metadata import version as pkgversion
from pathlib import Path
from typing import TYPE_CHECKING

from duty import duty, tools

if TYPE_CHECKING:
    from collections.abc import Iterator

    from duty.context import Context

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "benchmark", "duties.py", "scripts"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
MULTIRUN = os.environ.get("MULTIRUN", "0") == "1"


def pyprefix(title: str) -> str:
    if MULTIRUN:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


@contextmanager
def material_insiders() -> Iterator[bool]:
    if "+insiders" in pkgversion("mkdocs-material"):
        os.environ["MATERIAL_INSIDERS"] = "true"
        try:
            yield True
        finally:
            os.environ.pop("MATERIAL_INSIDERS")
    else:
        yield False


def _get_changelog_version() -> str:
    changelog_version_re = re.compile(r"^## \[(\d+\.\d+\.\d+)\].*$")
    with Path(__file__).parent.joinpath("CHANGELOG.md").open("r", encoding="utf8") as file:
        return next(filter(bool, map(changelog_version_re.match, file))).group(1)  # type: ignore[union-attr]


@duty
def changelog(ctx: Context, bump: str = "") -> None:
    """Update the changelog in-place with latest commits.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(tools.git_changelog(bump=bump or None), title="Updating changelog")
    ctx.run(tools.yore.check(bump=bump or _get_changelog_version()), title="Checking legacy code")


@duty(pre=["check-quality", "check-types", "check-docs", "check-api"])
def check(ctx: Context) -> None:
    """Check it all!"""


@duty
def check_quality(ctx: Context) -> None:
    """Check the code quality.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml"),
        title=pyprefix("Checking code quality"),
    )


@duty
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)

    Path(".benchmarks").mkdir(parents=True, exist_ok=True)
    Path(".benchmarks/tmp.json").touch(exist_ok=True)

    ctx.run(
        tools.mkdocs.build(strict=False, verbose=True),
        title=pyprefix("Building documentation"),
        command="mkdocs build -vs",
    )


@duty
def check_types(ctx: Context) -> None:
    """Check that the code is correctly typed."""
    os.environ["FORCE_COLOR"] = "1"
    ctx.run(
        tools.mypy(*PY_SRC_LIST, config_file="config/mypy.ini"),
        title=pyprefix("Type-checking"),
    )


@duty
def check_api(ctx: Context, *cli_args: str) -> None:
    """Check for API breaking changes."""
    ctx.run(
        tools.griffe.check("variantplaner", search=["src"], color=True).add_args(*cli_args),
        title="Checking for API breaking changes",
        nofail=True,
    )


@duty(silent=True)
def clean(ctx: Context) -> None:
    """Delete temporary files.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf tests/.pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf htmlcov")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


@duty(post=["docs_build"])
def docs(ctx: Context) -> None:
    """Check if the documentation builds correctly."""
    ctx.run(
        tools.mkdocs.build(strict=False, verbose=True),
        title=pyprefix("Building documentation"),
    )


@duty
def docs_build(ctx: Context) -> None:
    """Deploy the documentation to GitHub pages."""
    with material_insiders():
        ctx.run(tools.mkdocs.build(), title="Build documentation")


@duty(post=["docs_build"])
def docs_deploy(ctx: Context) -> None:
    """Deploy the documentation on GitHub pages.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    os.environ["DEPLOY"] = "true"
    ctx.run(tools.mkdocs.gh_deploy(force=True), title="Deploying documentation")


@duty
def format(ctx: Context) -> None:
    """Run formatting tools on the code.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
        title="Auto-fixing code",
    )
    ctx.run(tools.ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")


@duty
def build(ctx: Context) -> None:
    """Build source and wheel distributions."""
    ctx.run(
        tools.build(),
        title="Building source and wheel distributions",
        pty=PTY,
    )


@duty
def publish(ctx: Context) -> None:
    """Publish source and wheel distributions to PyPI."""
    if not Path("dist").exists():
        ctx.run("false", title="No distribution files found")
    dists = [str(dist) for dist in Path("dist").iterdir()]
    ctx.run(
        tools.twine.upload(*dists, skip_existing=True),
        title="Publishing source and wheel distributions to PyPI",
        pty=PTY,
    )


@duty(post=["build", "publish", "docs-deploy"])
def release(ctx: Context, version: str = "") -> None:
    """Release a new Python package.

    Parameters:
        ctx: The context instance (passed automatically).
        version: The new version number to use.
    """
    ctx.run(
        "git add pyproject.toml CHANGELOG.md README.md src/variantplaner/__init__.py",
        title="Staging files",
        pty=PTY,
    )
    ctx.run(
        ["git", "commit", "-m", f"chore: Prepare release {version}"],
        title="Committing changes",
        pty=PTY,
    )
    ctx.run(f"git tag {version}", title="Tagging commit", pty=PTY)
    ctx.run("git push", title="Pushing commits", pty=False)
    ctx.run("git push --tags", title="Pushing tags", pty=False)


@duty(silent=True, aliases=["cov"])
def coverage(ctx: Context) -> None:
    """Report coverage as text and HTML."""
    ctx.run(tools.coverage.combine(), nofail=True)
    ctx.run(tools.coverage.report(rcfile="config/coverage.ini"), capture=False)
    ctx.run(tools.coverage.html(rcfile="config/coverage.ini"))


@duty
def test(ctx: Context, *cli_args: str, match: str = "") -> None:  # noqa: PT028
    """Run the test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        tools.pytest(
            "tests",
            config_file="config/pytest.ini",
            select=match,
            color="yes",
        ).add_args("-n", "auto", *cli_args),
        title=pyprefix("Running tests"),
    )


@duty
def bench(ctx: Context, *cli_args: str, match: str = "") -> None:
    """Run the benchmark test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    ctx.run(
        tools.pytest("benchmark", config_file="config/benchmark.ini", select=match, color="yes").add_args(*cli_args),
        title=pyprefix("Running benchmark"),
    )
