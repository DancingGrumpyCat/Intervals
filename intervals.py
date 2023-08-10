from typing import Self, Literal, Union
from collections.abc import Iterator

Number = Union[int, float]
IntervalType = Literal["closed", "open", "half-open"]

class Interval:
    epsilon = 1e-15
    def __init__(self, start: Number = 0, end: Number = 0, *, include_start = True, include_end = True) -> None:
        self.include_start = include_start
        self.include_end = include_end
        self._start = start
        self._end = end
        if not self.include_start:
            self.start = start + Interval.epsilon
        else:
            self.start = self._start
        if not self.include_end:
            self.end = end - Interval.epsilon
        else:
            self.end = self._end

    def __str__(self) -> str:
        if self._start == self._end:
            return str(self._start)
        l_bracket =  "[" if self.include_start else "("
        r_bracket =  "]" if self.include_end else ")"
        return "Interval" + l_bracket + str(self._start) + ", " + str(self._end) + r_bracket

    def step(self, step: float, start: float | None = None) -> Iterator[float]:
        if start is None:
            start = self._start
        while start < self.start:
            start += step
        while start <= self.end:
            yield start
            start += step

    @classmethod
    def from_plus_minus(cls, center: Number = 0, pm: Number = 0, s: str | None = None) -> Self:
        if s is not None:
            s = s.replace(" ", "").replace("/", "")
            center, pm = (float(x) for x in s.split("+-"))
        return Interval(start=(center - pm), end=(center + pm))

    @property
    def magnitude(self) -> float:
        return self._end - self._start

    @property
    def interval_type(self) -> IntervalType:
        if self.include_start and self.include_end:
            return "closed"
        elif not (self.include_start or self.include_end):
            return "open"
        return "half-open"
