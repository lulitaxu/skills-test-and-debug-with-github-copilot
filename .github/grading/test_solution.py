"""Additional behavior checks used by the exercise grader."""

from decimal import Decimal

import pytest

from src.bill_splitter import split_bill


@pytest.mark.parametrize(
    ("subtotal", "people", "tip_percent", "expected"),
    [
        (
            "0.05",
            2,
            0,
            [Decimal("0.03"), Decimal("0.02")],
        ),
        (
            Decimal("100.00"),
            6,
            Decimal("18"),
            [
                Decimal("19.67"),
                Decimal("19.67"),
                Decimal("19.67"),
                Decimal("19.67"),
                Decimal("19.66"),
                Decimal("19.66"),
            ],
        ),
        (
            1,
            8,
            0,
            [
                Decimal("0.13"),
                Decimal("0.13"),
                Decimal("0.13"),
                Decimal("0.13"),
                Decimal("0.12"),
                Decimal("0.12"),
                Decimal("0.12"),
                Decimal("0.12"),
            ],
        ),
    ],
)
def test_all_cents_are_distributed(subtotal, people, tip_percent, expected):
    assert split_bill(subtotal, people, tip_percent) == expected


def test_total_is_rounded_once_before_distribution():
    shares = split_bill("0.03", 2, "16.67")
    assert shares == [Decimal("0.02"), Decimal("0.02")]
    assert sum(shares) == Decimal("0.04")


def test_every_share_is_quantized_to_cents():
    shares = split_bill("3.00", 7)
    assert all(share.as_tuple().exponent == -2 for share in shares)


@pytest.mark.parametrize("value", ["-0.01", Decimal("-1"), -0.1])
def test_negative_subtotals_remain_invalid(value):
    with pytest.raises(ValueError, match="subtotal"):
        split_bill(value, 2)
