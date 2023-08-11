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
        includes_lower_bound: bool = True,
        includes_upper_bound: bool = True,
    ) -> None:
        # Put start & end in the right order
        if start > end:
            start, end = end, start
            includes_upper_bound, includes_lower_bound = (
                includes_lower_bound,
                includes_upper_bound,
            )

        # Lower and upper bound boolean flags (unbounded sides must be closed)
        self.includes_lower_bound = includes_lower_bound or abs(start) == float("inf")
        self.includes_upper_bound = includes_upper_bound or abs(end) == float("inf")

        # The presented values of the bounds
        self.apparent_start = start
        self.apparent_end = end

        # The actual values of the bounds adjusted by a tiny number
        # TODO: this number's magnitude should depend on the Interval bound magnitude
        if not self.includes_lower_bound:
            self.actual_start: Number = start + Interval.epsilon
        else:
            self.actual_start = self.apparent_start
        if not self.includes_upper_bound:
            self.actual_end: Number = end - Interval.epsilon
        else:
            self.actual_end = self.apparent_end

    def __str__(self) -> str:
        if self.magnitude == 0:
            return "∅"
        if self.apparent_start == self.apparent_end:
            return str(self.apparent_start)
        s, e = self.apparent_start, self.apparent_end
        l_bracket: str = "[" if self.includes_lower_bound else "("
        r_bracket: str = "]" if self.includes_upper_bound else ")"
        return f"{l_bracket}{s}, {e}{r_bracket}"

    def __repr__(self) -> str:
        s, e = self.apparent_start, self.apparent_end
        i_s: bool = self.includes_lower_bound
        i_e: bool = self.includes_upper_bound
        return f"Interval(start={s}, end={e}, include_start={i_s}, include_end={i_e})"

    def __contains__(self, value: Number) -> bool:
        return self.actual_start <= value <= self.actual_end

    def __eq__(self, other: Interval) -> bool:
        return all(
            [
                self.actual_start == other.actual_start,
                self.actual_end == other.actual_end,
                self.includes_lower_bound == other.includes_lower_bound,
                self.includes_upper_bound == other.includes_upper_bound,
            ]
        )

    def step(
        self,
        step: float,
        start: float | None = None,
    ) -> Iterator[float]:
        """
        ### Description
        A generator function that, like Python's default `range`, yields values between
        `start` and `stop`, with step `step`.
        """
        if start is None:
            start = self.actual_start
        start %= step
        if step == 0:
            raise ValueError("step must be non-zero")
        while start in self:
            yield start
            start += step

    def __invert__(self) -> Interval:
        return Interval(
            self.actual_start,
            self.actual_end,
            includes_lower_bound=not self.includes_lower_bound,
            includes_upper_bound=not self.includes_upper_bound,
        )

    def __add__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start + value,
            self.apparent_end + value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __sub__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start - value,
            self.apparent_end - value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __mul__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start * value,
            self.apparent_end * value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __truediv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start / value,
            self.apparent_end / value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __floordiv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_start // value,
            self.apparent_end // value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def intersects(self, other: Interval) -> bool:
        return (
            other.apparent_start > self.apparent_end
            or self.apparent_start > other.apparent_end
        )

    def __and__(self, other: Interval) -> Interval:
        if self.intersects(other):
            return EMPTY_SET
        return Interval(
            max(self.apparent_start, other.apparent_start),
            min(self.apparent_end, other.apparent_end),
        )

    def __or__(self, other: Interval) -> Interval:
        if self.intersects(other):
            raise ValueError(
                "intervals must intersect or be adjacent to create a union"
            )
        min_lower_bounded = self if self.actual_start < other.actual_start else other
        max_upper_bounded = self if self.actual_end > other.actual_end else other
        return Interval(
            min(self.apparent_start, other.apparent_start),
            max(self.apparent_end, other.apparent_end),
            includes_lower_bound=min_lower_bounded.includes_lower_bound,
            includes_upper_bound=max_upper_bounded.includes_upper_bound,
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
            s = (
                s.replace(" ", "")
                .replace("/", "")
                .replace("±", "+-")
                .replace("pm", "+-")
            )
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
        if self.includes_lower_bound and self.includes_upper_bound:
            return "closed"
        if not (self.includes_lower_bound or self.includes_upper_bound):
            return "open"
        return "half-open"


EMPTY_SET = Interval(0, 0, includes_lower_bound=False, includes_upper_bound=False)
