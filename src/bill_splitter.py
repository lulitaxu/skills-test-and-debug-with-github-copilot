"""Split a bill into predictable, currency-safe shares."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ONE_HUNDRED = Decimal("100")


def split_bill(
    subtotal: Decimal | str | int | float,
    people: int,
    tip_percent: Decimal | str | int | float = 0,
) -> list[Decimal]:
    """Return shares of a subtotal plus tip, each rounded to cents."""
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

    # Work in integer cents so no cent is lost or invented: give one
    # extra cent to each of the earliest shares until the remainder
    # from the division is exhausted.
    total_cents = int(total * ONE_HUNDRED)
    base_cents, remainder_cents = divmod(total_cents, people)
    return [
        (Decimal(base_cents + (1 if index < remainder_cents else 0)) / ONE_HUNDRED).quantize(CENT)
        for index in range(people)
    ]
