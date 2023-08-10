from __future__ import annotations
from typing import Literal, Union
from random import random
from collections.abc import Iterator

Number = Union[int, float]
IntervalType = Literal["closed", "open", "half-open"]


class Interval:
    epsilon = 1e-15

    def __init__(
        self,
        start: Number = 0,
        end: Number = 0,
        *,
        include_start: bool = True,
        include_end: bool = True,
    ) -> None:
        if start > end:
            raise ValueError(f"lower bound {start} greater than upper bound {end}")
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
        l_bracket = "[" if self.include_start else "("
        r_bracket = "]" if self.include_end else ")"
        return f"Interval<{l_bracket}{self._start}, {self._end}{r_bracket}>"

    def __repr__(self) -> str:
        "Interval(0, 5, include_start=False)"

    def __contains__(self, value: Number) -> bool:
        return self.start <= value <= self.end

    def step(self, step: float, start: float | None = None) -> Iterator[float]:
        if start is None:
            start = self._start
        while start < self.start:
            start += step
        while start <= self.end:
            yield start
            start += step

    def __invert__(self) -> Interval:
        return Interval(
            self.start,
            self.end,
            include_start=not self.include_start,
            include_end=not self.include_end,
        )

    def __add__(self, value: Number) -> Interval:
        """
        Raises each of start and end by a value.
        """
        return Interval(
            self._start + value,
            self._end + value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __sub__(self, value: Number) -> Interval:
        """
        Lowers each of start and end by a value.
        """
        return Interval(
            self._start - value,
            self._end - value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __mul__(self, value: Number) -> Interval:
        """
        Multiplies each of start and end by a value.
        """
        return Interval(
            self._start * value,
            self._end * value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __truediv__(self, value: Number) -> Interval:
        """
        Divides (using float division) each of start and end by a value.
        """
        return Interval(
            self._start / value,
            self._end / value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __floordiv__(self, value: Number) -> Interval:
        """
        Divides and floors each of start and end by a value.
        """
        return Interval(
            self._start // value,
            self._end // value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    @classmethod
    def from_plus_minus(
        cls, center: Number = 0, pm: Number = 0, s: str | None = None
    ) -> Interval:
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
