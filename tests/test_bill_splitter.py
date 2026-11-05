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


def test_even_split():
    assert split_bill("42.00", 3) == [
        Decimal("14.00"),
        Decimal("14.00"),
        Decimal("14.00"),
    ]


def test_tip_is_included():
    assert split_bill("80.00", 4, 25) == [
        Decimal("25.00"),
        Decimal("25.00"),
        Decimal("25.00"),
        Decimal("25.00"),
    ]


def test_remainder_pennies_are_distributed():
    assert split_bill("10.00", 3) == [
        Decimal("3.34"),
        Decimal("3.33"),
        Decimal("3.33"),
    ]


def test_tip_rounding_preserves_every_cent():
    assert split_bill("10.01", 3, 20) == [
        Decimal("4.01"),
        Decimal("4.00"),
        Decimal("4.00"),
    ]
