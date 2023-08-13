from collections.abc import Iterator

from intervals.intervals import Interval

_INF = float("inf")


UNIT: Interval = Interval(0, 1)
NEGATIVE_UNIT: Interval = Interval(-1, 0)
UNIT_DISK: Interval = NEGATIVE_UNIT | UNIT
POSITIVE_REALS: Interval = Interval(0, _INF)
NATURALS: Iterator[int] = map(int, POSITIVE_REALS.step(1))
WHOLE_NUMBERS: Iterator[int] = map(int, (POSITIVE_REALS + 1).step(1))
PI = Interval(223 / 71, 22 / 7, lower_closure="open", upper_closure="open")
