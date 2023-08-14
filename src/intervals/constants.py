from collections.abc import Iterator

from intervals.intervals import Interval

_INF = float("inf")

ADDITIVE_IDENTITY: Interval = Interval(
    +0,
    +0,
    lower_closure="closed",
    upper_closure="closed",
)
UNIT: Interval = Interval(
    +0,
    +1,
    lower_closure="open",
    upper_closure="closed",
)
NEGATIVE_UNIT: Interval = Interval(
    -1,
    +0,
    lower_closure="closed",
    upper_closure="open",
)
UNIT_DISK: Interval = Interval(
    -1,
    +1,
    lower_closure="closed",
    upper_closure="closed",
)
POSITIVE_REALS: Interval = Interval(
    +0,
    +_INF,
    lower_closure="open",
    upper_closure="closed",
)
NATURALS: Iterator[int] = map(int, POSITIVE_REALS.step(1))
WHOLE_NUMBERS: Iterator[int] = map(int, (POSITIVE_REALS + 1).step(1))
PI = Interval(223 / 71, 22 / 7, lower_closure="open", upper_closure="open")
