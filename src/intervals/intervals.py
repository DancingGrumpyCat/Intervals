from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from collections.abc import Iterator

Number = Union[int, float]
"""A type alias for the float | int union."""
IntervalType = Literal["closed", "open", "half-open"]
"""
Intervals can be closed (on both ends), open (on both ends), or half-open
(open on one end and closed on the other).
"""


class Interval:
    """
    ### Description
    An Interval has a start and end value, and two booleans indicating closed/open state
    for each bound. The start value is the lower bound and the end value is the upper
    bound.
    ### Example
    ```py
    x = Interval(0, 5, include_start=True)
    ```
    ### List of methods
    - __init__
    - __str__
    - __repr__
    - step
    - __invert__
    - __add__
    - __sub__
    - __mul__
    - __truediv__
    - __floordiv__
    - from_plus_minus (class method)
    - magnitude (property)
    - interval_type (property)

    """

    epsilon = 1e-15  # TODO: change this out for something like math.nextfloat

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
        self.apparent_start = start
        self.apparent_end = end
        if not self.include_start:
            self.actual_start: Number = start + Interval.epsilon
        else:
            self.actual_start = self.apparent_start
        if not self.include_end:
            self.actual_end: Number = end - Interval.epsilon
        else:
            self.actual_end = self.apparent_end

    def __str__(self) -> str:
        if self.magnitude == 0:
            return "∅"
        if self.apparent_start == self.apparent_end:
            return str(self.apparent_start)
        s, e = self.apparent_start, self.apparent_end
        l_bracket: str = "[" if self.include_start else "("
        r_bracket: str = "]" if self.include_end else ")"
        return f"{l_bracket}{s}, {e}{r_bracket}"

    def __repr__(self) -> str:
        s, e = self.apparent_start, self.apparent_end
        i_s: bool = self.include_start
        i_e: bool = self.include_end
        return f"Interval({s}, {e}, {i_s}, {i_e})"

    def __contains__(self, value: Number) -> bool:
        return self.actual_start <= value <= self.actual_end

    def step(self, step: float, start: float | None = None) -> Iterator[float]:
        """
        ### Description
        A generator function that, like Python's default `range`, yields values between
        `start` and `stop`, with step `step`.
        """
        if step <= 0:
            raise ValueError("step must be greater than 0")
        if start is None:
            start = self.apparent_start
        start %= step
        while start <= self.actual_end:
            yield start
            start += step

    def __invert__(self) -> Interval:
        return Interval(
            self.actual_start,
            self.actual_end,
            include_start=not self.include_start,
            include_end=not self.include_end,
        )

    def __add__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start + value,
            self.apparent_end + value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __sub__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start - value,
            self.apparent_end - value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __mul__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start * value,
            self.apparent_end * value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __truediv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start / value,
            self.apparent_end / value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def __floordiv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start // value,
            self.apparent_end // value,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    @classmethod
    def from_plus_minus(
        cls, center: Number = 0, plusminus: Number = 0, s: str | None = None
    ) -> Interval:
        """
        ### Description
        An additional class method to initialize an Interval instance in "plus/minus"
        style. Alternatively you can enter it as a string.
        ### Example
        ```py
        x = Interval.from_plus_minus(4, 0.5) # 4 ± 0.5
        x = Interval.from_plus_minus(s="4±0.5")
        ```
        """
        if s is not None:
            s = s.replace(" ", "").replace("/", "").replace("±", "+-")
            center, plusminus = (float(x) for x in s.split("+-"))
        return Interval(start=(center - plusminus), end=(center + plusminus))

    @property
    def magnitude(self) -> float:
        """
        The positive difference between the apparent lower and upper bounds.
        """
        return self.apparent_end - self.apparent_start

    @property
    def interval_type(self) -> IntervalType:
        if self.include_start and self.include_end:
            return "closed"
        if not (self.include_start or self.include_end):
            return "open"
        return "half-open"
