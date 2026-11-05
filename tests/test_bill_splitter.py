from decimal import Decimal

import pytest

from src.bill_splitter import split_bill


def test_zero_subtotal_returns_zero_shares():
    assert split_bill("0", 2) == [Decimal("0.00"), Decimal("0.00")]


@pytest.mark.parametrize("people", [0, -1, 2.5, True])
def test_people_must_be_a_positive_integer(people):
    with pytest.raises(ValueError, match="positive integer"):
        split_bill("10.00", people)


@pytest.mark.parametrize(
    ("subtotal", "tip_percent", "message"),
    [
        ("-0.01", 0, "subtotal"),
        ("10.00", "-1", "tip_percent"),
    ],
)
def test_negative_money_values_are_rejected(subtotal, tip_percent, message):
    with pytest.raises(ValueError, match=message):
        split_bill(subtotal, 2, tip_percent)
