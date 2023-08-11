from __future__ import annotations

from typing import TYPE_CHECKING, Union, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Callable

Number = Union[int, float]
"""A type alias for the float | int union."""
IntervalType = Literal["closed", "open", "half-open"]
"""
Intervals can be closed (on both ends), open (on both ends), or half-open
(open on one end and closed on the other).
"""
_INF = float("inf")


# TODO: add fuzzy interval class, derived from Interval, with a membership function.
# Figure out logic & arithmetic between such fuzzy sets
# Source:
# -  L.A. Zadeh,
# -  Fuzzy sets, Information and Control, Volume 8, Issue 3, 1965, Pages 338-353.
# -  ISSN 0019-9958.
# -  https://doi.org/10.1016/S0019-9958(65)90241-X.


class Interval:
    """
    ### Description
    An Interval has a start and end value, and two booleans indicating closed/open state
    for each bound. The start value is the lower bound and the end value is the upper
    bound. Each of `start` and `end` may be finite or infinite, with some restrictions
    on which methods are then available to use.
    """

    _epsilon = 1e-15  # TODO: change this out for something like math.nextfloat

    def __init__(
        self,
        lower_bound: Number = 0,
        upper_bound: Number = 0,
        *,
        includes_lower_bound: bool = True,
        includes_upper_bound: bool = True,
    ) -> None:
        # Put start & end in the right order
        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound
            includes_upper_bound, includes_lower_bound = (
                includes_lower_bound,
                includes_upper_bound,
            )

        # Lower and upper bound boolean flags (unbounded sides must be closed)
        self.includes_lower_bound: bool = (
            includes_lower_bound or abs(lower_bound) == _INF
        )
        self.includes_upper_bound: bool = (
            includes_upper_bound or abs(upper_bound) == _INF
        )

        # The presented values of the bounds
        self.apparent_lower_bound = lower_bound
        self.apparent_upper_bound = upper_bound

        # The actual values of the bounds adjusted by a tiny number
        # TODO: this number's magnitude should depend somehow on the magnitude of the
        # interval's bounds
        if not self.includes_lower_bound:
            self.lower_bound: Number = lower_bound + Interval._epsilon
        else:
            self.lower_bound = self.apparent_lower_bound
        if not self.includes_upper_bound:
            self.upper_bound: Number = upper_bound - Interval._epsilon
        else:
            self.upper_bound = self.apparent_upper_bound

    def __str__(self) -> str:
        if self.diameter == 0:
            return "∅"
        if self.apparent_lower_bound == self.apparent_upper_bound:
            return str(self.apparent_lower_bound)
        s, e = self.apparent_lower_bound, self.apparent_upper_bound
        l_bracket: str = "[" if self.includes_lower_bound else "("
        r_bracket: str = "]" if self.includes_upper_bound else ")"
        return f"{l_bracket}{s}, {e}{r_bracket}"

    def __repr__(self) -> str:
        s, e = self.apparent_lower_bound, self.apparent_upper_bound
        i_s: bool = self.includes_lower_bound
        i_e: bool = self.includes_upper_bound
        return f"Interval(start={s}, end={e}, include_start={i_s}, include_end={i_e})"

    def __contains__(self, value: Number) -> bool:
        return self.lower_bound <= value <= self.upper_bound

    def __eq__(self, other: Interval) -> bool:
        return all(
            [
                self.lower_bound == other.lower_bound,
                self.upper_bound == other.upper_bound,
                self.includes_lower_bound == other.includes_lower_bound,
                self.includes_upper_bound == other.includes_upper_bound,
            ]
        )

    def truncate(self, precision: int) -> Interval:
        # floor and ceil with precision argument
        def _floor(_x: Number, _p: int) -> int:
            return round(_x - 0.5 * 10**-_p, _p)

        def _ceil(_x: Number, _p: int) -> int:
            return round(_x + 0.5 * 10**-_p, _p)

        # The lower bound and upper bound must be lowered and raised respectively,
        # expanding the interval, because the output interval needs to be a (non-strict)
        # superset of the input interval.
        # Its lower and upper bounds close because it's being truncated.
        return Interval(
            _floor(self.apparent_lower_bound, _p=precision),
            _ceil(self.apparent_upper_bound, _p=precision),
            includes_lower_bound=True,
            includes_upper_bound=True,
        )

    def step(
        self,
        step: float,
        start: float | None = None,
    ) -> Iterator[float]:
        """
        ### Description
        A generator function that, like Python's default `range`, yields values between
        `start` and `stop`, with step `step`. Note that if the lower bound is
        &minus;infinity, you must pass a `start` value and count downwards (with a
        negative step value) instead of starting from &minus;infinity.
        """
        if start is None:
            start = self.lower_bound
        start %= step
        if step == 0:
            raise ValueError("step must be non-zero")
        while start in self:
            yield start
            start += step

    def __invert__(self) -> Interval:
        return Interval(
            self.lower_bound,
            self.upper_bound,
            includes_lower_bound=not self.includes_lower_bound,
            includes_upper_bound=not self.includes_upper_bound,
        )

    def __add__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_lower_bound + value,
            self.apparent_upper_bound + value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __sub__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_lower_bound - value,
            self.apparent_upper_bound - value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __mul__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_lower_bound * value,
            self.apparent_upper_bound * value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __truediv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_lower_bound / value,
            self.apparent_upper_bound / value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def __floordiv__(self, value: Number) -> Interval:
        return Interval(
            self.apparent_lower_bound // value,
            self.apparent_upper_bound // value,
            includes_lower_bound=self.includes_lower_bound,
            includes_upper_bound=self.includes_upper_bound,
        )

    def intersects(self, other: Interval) -> bool:
        return (
            other.apparent_lower_bound > self.apparent_upper_bound
            or self.apparent_lower_bound > other.apparent_upper_bound
        )

    def __and__(self, other: Interval) -> Interval:
        if self.intersects(other):
            return EMPTY_SET
        return Interval(
            max(self.apparent_lower_bound, other.apparent_lower_bound),
            min(self.apparent_upper_bound, other.apparent_upper_bound),
        )

    def __or__(self, other: Interval) -> Interval:
        if self.intersects(other):
            raise ValueError(
                "intervals must intersect or be adjacent to create a union"
            )
        min_lower_bounded = self if self.lower_bound < other.lower_bound else other
        max_upper_bounded = self if self.upper_bound > other.upper_bound else other
        return Interval(
            min(self.apparent_lower_bound, other.apparent_lower_bound),
            max(self.apparent_upper_bound, other.apparent_upper_bound),
            includes_lower_bound=min_lower_bounded.includes_lower_bound,
            includes_upper_bound=max_upper_bounded.includes_upper_bound,
        )

    def binary_fn(
        self, other: Interval, fn: Callable[[Number, Number], Number]
    ) -> Interval:
        """
        ### Description
        Combines two intervals with an arbitrary binary function. Recommended to use
        this with the `operator` module.

        Currently only supports closed intervals.
        """
        x1, x2, y1, y2 = (
            self.apparent_lower_bound,
            self.apparent_upper_bound,
            other.apparent_lower_bound,
            other.apparent_upper_bound,
        )
        possible_bounds: list[Number] = [fn(x1, y1), fn(x1, y2), fn(x2, y1), fn(x2, y2)]
        return Interval(
            min(possible_bounds),
            max(possible_bounds),
            includes_lower_bound=True,
            includes_upper_bound=True,
        )

    @classmethod
    def from_plus_minus(
        cls, center: Number = 0, plusminus: Number = 0, *, string: str = ""
    ) -> Interval:
        """
        ### Description
        An additional class method to initialize an Interval instance in "plus/minus"
        style. Alternatively you can enter it as a string.

        The resulting interval is half-open (has a closed lower bound and an open
        upper bound).

        ### Example
        (More examples available in the README.)
        ```py
        >>> Interval.from_plus_minus(4, 0.5)
        # [3.5, 4.5)
        ```
        """
        if not (center or plusminus):
            if string == "":
                raise ValueError("no values were passed")
            string = (
                string.replace(" ", "")
                .replace("/", "")
                .replace("±", "+-")
                .replace("pm", "+-")
            )
            center, plusminus = (float(x) for x in string.split("+-"))
        return Interval(
            lower_bound=(center - plusminus),
            upper_bound=(center + plusminus),
            includes_upper_bound=False,
        )

    @property
    def diameter(self) -> float:
        """
        The positive difference between the apparent lower and upper bounds.
        """
        return self.apparent_upper_bound - self.apparent_lower_bound

    @property
    def interval_type(self) -> IntervalType:
        if self.includes_lower_bound and self.includes_upper_bound:
            return "closed"
        if not (self.includes_lower_bound or self.includes_upper_bound):
            return "open"
        return "half-open"

    @property
    def midpoint(self) -> float:
        return (self.apparent_lower_bound + self.apparent_upper_bound) / 2

    def as_plus_minus(self, *, precision: int = 3) -> str:
        return (
            f"{round(self.midpoint, precision)} ± "
            f"{round(self.apparent_upper_bound - self.midpoint, precision)}"
        )


EMPTY_SET = Interval(0, 0, includes_lower_bound=False, includes_upper_bound=False)
