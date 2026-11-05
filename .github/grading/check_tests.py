"""Check learner-authored tests without depending on prompt wording."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

TEST_FILE = Path("tests/test_bill_splitter.py")
FOCUSED_TESTS = {"test_even_split", "test_tip_is_included"}
EDGE_TESTS = {
    "test_remainder_pennies_are_distributed",
    "test_tip_rounding_preserves_every_cent",
}

BUGGY_IMPLEMENTATION = '''\
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ONE_HUNDRED = Decimal("100")

def split_bill(subtotal, people, tip_percent=0):
    if isinstance(people, bool) or not isinstance(people, int) or people <= 0:
        raise ValueError("people must be a positive integer")
    subtotal_amount = Decimal(str(subtotal))
    tip_rate = Decimal(str(tip_percent))
    if subtotal_amount < 0:
        raise ValueError("subtotal cannot be negative")
    if tip_rate < 0:
        raise ValueError("tip_percent cannot be negative")
    tip = subtotal_amount * tip_rate / ONE_HUNDRED
    total = (subtotal_amount + tip).quantize(CENT, rounding=ROUND_HALF_UP)
    share = (total / people).quantize(CENT, rounding=ROUND_HALF_UP)
    return [share] * people
'''

ZERO_IMPLEMENTATION = BUGGY_IMPLEMENTATION.replace(
    "share = (total / people).quantize(CENT, rounding=ROUND_HALF_UP)",
    'share = Decimal("0.00")',
)

FIXED_IMPLEMENTATION = BUGGY_IMPLEMENTATION.replace(
    """\
    share = (total / people).quantize(CENT, rounding=ROUND_HALF_UP)
    return [share] * people""",
    """\
    total_cents = int(total * ONE_HUNDRED)
    base_cents, remainder = divmod(total_cents, people)
    return [
        (Decimal(base_cents + (index < remainder)) / ONE_HUNDRED).quantize(CENT)
        for index in range(people)
    ]""",
)


def test_names() -> set[str]:
    if not TEST_FILE.is_file():
        return set()
    tree = ast.parse(TEST_FILE.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def run_pytest(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def run_with_implementation(
    implementation: str, expression: str
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "bill_splitter.py").write_text(
            implementation, encoding="utf-8"
        )
        shutil.copy2(TEST_FILE, root / TEST_FILE)
        return run_pytest(
            "tests/test_bill_splitter.py", "-k", expression, cwd=root
        )


def check_focused(names: set[str]) -> int:
    missing = FOCUSED_TESTS - names
    if missing:
        print(f"Missing focused tests: {', '.join(sorted(missing))}")
        return 1

    expression = "even_split or tip_is_included"
    correct_result = run_with_implementation(BUGGY_IMPLEMENTATION, expression)
    mutation_result = run_with_implementation(ZERO_IMPLEMENTATION, expression)
    print(correct_result.stdout, end="")
    if correct_result.returncode:
        print(correct_result.stderr, end="")
        print("Both focused tests must pass before moving to edge cases.")
        return 1
    if mutation_result.returncode != 1 or not all(
        name in mutation_result.stdout for name in FOCUSED_TESTS
    ):
        print("Both focused tests must detect an implementation returning zero shares.")
        return 1
    print("Both focused tests pass for correct behavior and reject a broken result.")
    return 0


def check_edges(names: set[str]) -> int:
    missing = EDGE_TESTS - names
    if missing:
        print(f"Missing edge-case tests: {', '.join(sorted(missing))}")
        return 1

    expression = " or ".join(name.removeprefix("test_") for name in EDGE_TESTS)
    buggy_result = run_with_implementation(BUGGY_IMPLEMENTATION, expression)
    fixed_result = run_with_implementation(FIXED_IMPLEMENTATION, expression)

    print(buggy_result.stdout, end="")
    if buggy_result.returncode != 1:
        print(buggy_result.stderr, end="")
        print("The edge tests must fail against the known-buggy implementation.")
        return 1
    if not all(name in buggy_result.stdout for name in EDGE_TESTS):
        print("Both required edge tests must be collected and expose the defect.")
        return 1
    if fixed_result.returncode:
        print(fixed_result.stdout, end="")
        print(fixed_result.stderr, end="")
        print("The edge tests must pass against the corrected behavior.")
        return 1
    print("Both edge tests detect the defect and accept the corrected behavior.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("focused", "edges"))
    phase = parser.parse_args().phase
    try:
        names = test_names()
    except (OSError, SyntaxError) as error:
        print(f"Could not read tests: {error}")
        return 1
    return check_focused(names) if phase == "focused" else check_edges(names)


if __name__ == "__main__":
    sys.exit(main())
