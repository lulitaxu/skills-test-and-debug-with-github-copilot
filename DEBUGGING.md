# Debugging notes

## What the code does

The `split_bill` function in `src/bill_splitter.py` takes a subtotal, a number of people, and an optional tip percentage. It validates that `people` is a positive integer (rejecting booleans, floats, zero, and negatives) and that neither the subtotal nor the tip percentage is negative. It converts the money inputs to `Decimal` through `str()`, computes the tip, and rounds the combined total once to cents. Then it divides that rounded total by the number of people, rounds the resulting share to cents on its own, and returns a list containing that same share repeated once per person.

## Baseline evidence

I ran `python -m pytest -q` on the unmodified code before making any changes. All 7 existing tests passed. Those tests cover a zero subtotal, invalid `people` values, and negative subtotal or tip values, but every money case in them either is zero or divides evenly, so the passing baseline does not say anything about totals that leave a remainder when divided.

## Hypothesis

The bug is the per-share rounding step: `share = (total / people).quantize(CENT, rounding=ROUND_HALF_UP)` rounds one share and then repeats it, so the shares can add up to less (or more) than the rounded total. Specifically, splitting $10.00 among 3 people should produce shares summing to $10.00, but the current code returns $3.33 three times, which sums to $9.99 and loses a cent. A test asserting that $10.00 split among 3 people returns [3.34, 3.33, 3.33] would fail against the current code if this hypothesis is right, and pass only if the lost cent is distributed to one of the shares.
