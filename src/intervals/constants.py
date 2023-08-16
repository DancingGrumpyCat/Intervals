from collections.abc import Iterator

from intervals.intervals import Interval

_INF = float("inf")

UNIT: Interval = Interval(1)

UNIT_DISK: Interval = ~(UNIT | -UNIT)

POSITIVE_REALS: Interval = Interval(_INF).closed()

NATURALS: Iterator[int] = map(int, POSITIVE_REALS.step(1))
WHOLE_NUMBERS: Iterator[int] = map(int, (POSITIVE_REALS + 1).step(1))
PI: Interval = Interval.from_string(f"({223 / 71}, {22 / 7})")
