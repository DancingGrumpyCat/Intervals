from collections.abc import Iterator

from intervals.intervals import Interval

UNIT = Interval(1)

UNIT_DISK = ~(UNIT | -UNIT)

POSITIVE_REALS = Interval(float("inf")).closed()

NATURALS: Iterator[int] = (int(x) for x in POSITIVE_REALS.step(1))
WHOLE_NUMBERS: Iterator[int] = (int(x) for x in (POSITIVE_REALS + 1).step(1))
PI = Interval.from_string(f"({223 / 71}, {22 / 7})")
