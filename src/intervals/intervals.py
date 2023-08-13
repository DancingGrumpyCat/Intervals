########################################################################################
#                                        IMPORTS                                       #
########################################################################################

from __future__ import annotations

import operator as op
from math import copysign
from typing import TYPE_CHECKING, Any, Literal, Union

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import NotImplementedType

########################################################################################
#                                       CONSTANTS                                      #
########################################################################################

Number = Union[int, float]
"""A type alias for the `float | int` union."""

IntervalType = Literal["closed", "open", "half-open"]
"""
Intervals can be closed (on both ends), open (on both ends), or half-open
(open on one end and closed on the other).
"""

EPSILON: Number = 1e-15
_INF: Number = float("inf")

########################################################################################
#                                  BOUNDS HELPER CLASS                                 #
########################################################################################


class Bounds:
    def __init__(
        self,
        lower_bound: Number = 0,
        upper_bound: Number = 0,
        /,
        *,
        lower_closure: IntervalType = "closed",
        upper_closure: IntervalType = "closed",
    ) -> None:
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self.lower_closure = lower_closure
        self.upper_closure = upper_closure

        # The actual values of the bounds adjusted by a tiny number
        # TODO: this number's magnitude should depend somehow on the magnitude of the
        # interval's bounds
        self.adjusted_lower_bound: Number = lower_bound + EPSILON * (
            lower_closure == "open"
        )
        self.adjusted_upper_bound: Number = upper_bound - EPSILON * (
            upper_closure == "open"
        )


########################################################################################
#                                      MAIN CLASS                                      #
########################################################################################


class Interval:
    """
    ### Description
    An Interval has a start and end value, and two booleans indicating closed/open state
    for each bound. Each of `start` and `end` may be finite or infinite, with some rest-
    rictions on which methods are then available to use.
    """

    ####################################### INIT #######################################

    def __init__(
        self,
        lower_bound: Number,
        upper_bound: Number,
        /,
        *,
        lower_closure: IntervalType = "closed",
        upper_closure: IntervalType = "closed",
    ) -> None:
        # Initialize bounds
        bounds = Bounds(
            lower_bound,
            upper_bound,
            lower_closure=lower_closure,
            upper_closure=upper_closure,
        )

        # Put start & end in the right order
        # TODO: make a helper class for each bounding side
        if bounds.lower_bound > bounds.upper_bound:
            bounds.lower_bound, bounds.upper_bound = (
                bounds.upper_bound,
                bounds.lower_bound,
            )
            bounds.lower_closure, bounds.upper_closure = (
                bounds.upper_closure,
                bounds.lower_closure,
            )
            bounds.adjusted_lower_bound, bounds.adjusted_upper_bound = (
                bounds.adjusted_upper_bound,
                bounds.adjusted_lower_bound,
            )

        # The presented values of the bounds
        self.lower_bound = bounds.lower_bound
        self.upper_bound = bounds.upper_bound

        # Lower and upper bound interval type (unbounded sides must be closed)
        # Interval type is either closed or open
        self.lower_closure: IntervalType = (
            "closed" if abs(bounds.lower_bound) == _INF else bounds.lower_closure
        )
        self.upper_closure: IntervalType = (
            "closed" if abs(bounds.upper_bound) == _INF else bounds.upper_closure
        )

        self.adjusted_lower_bound = bounds.adjusted_lower_bound
        self.adjusted_upper_bound = bounds.adjusted_upper_bound

    @classmethod
    def from_plus_minus(
        cls, center: Number = 0, plusminus: Number = 0, *, string: str = ""
    ) -> Interval:
        """
        ### Description
        An additional initialization method in "plus/minus" style. Alternatively you can
        enter it as a string.

        The output interval is half-open; it has a closed lower and an open upper bound.

        ### Example
        (More examples available in the README.)
        ```py
        >>> Interval.from_plus_minus(4, 0.5)
        # [3.5, 4.5)
        ```
        """
        if not (center or plusminus):
            if not string:
                raise ValueError("no values were passed")
            string = (
                string.replace(" ", "")
                .replace("/", "")
                .replace("±", "+-")
                .replace("pm", "+-")
            )
            center, plusminus = map(float, string.split("+-"))
        return Interval(center - plusminus, center + plusminus, upper_closure="open")

    #################################### PROPERTIES ####################################

    @property
    def diameter(self) -> float:
        """
        ### Description
        The positive difference between the apparent lower and upper bounds.
        """
        return self.upper_bound - self.lower_bound

    @property
    def interval_type(self) -> IntervalType:
        """
        ### Description
        The type of interval can be `"closed"` (if both bounds are closed), `"open"` (if
        both bounds are open), or `"half-open"` (if neither of the above is true).
        """
        if self.lower_closure == self.upper_closure == "closed":
            return "closed"
        if self.lower_closure == self.upper_closure == "open":
            return "open"
        return "half-open"

    @property
    def midpoint(self) -> float:
        """
        ### Description
        Returns the arithmetic average of the two bounds, treating each as closed.
        """
        return (self.lower_bound + self.upper_bound) / 2

    ################################## NORMAL METHODS ##################################

    def as_plus_minus(self, *, precision: int = 3) -> str:
        """
        ### Description
        Returns a string representing an interval in plus-minus form.

        ### Example
        `[-1, 7] -> "3 ± 4"`. Loses information about whether the bounds are closed.
        """
        return (
            f"{round(self.midpoint, precision)} ± "
            f"{round(self.upper_bound - self.midpoint, precision)}"
        )

    def step(
        self,
        step: float,
        start: float | None = None,
    ) -> Iterator[float]:
        """
        ### Description
        A generator. Like Python's default `range`, it yields values between `start` and
        `stop`, adding `step` each time. Note that if the lower bound is &minus;&infin;,
        you must pass the `start` which is normally optional, and the step value must be
        negative, since you can't start counting from &minus;&infin;.

        The method will raise a `ValueError` if step is zero.
        """
        if start is None:
            start = self.lower_bound
        if start not in self:
            start = self.lower_bound + start % step
        if step == 0:
            raise ValueError("step must be non-zero")
        counter = 1
        current: Number = start
        while current in self:
            yield current
            current = start + counter * step
            counter += 1

    def steps(self, subdivisions: Number) -> Iterator[Number]:
        """
        ### Description
        Creates an iterator out of uniform subdivisions of the interval. If subdivisions
        is not an integer, the last subdivision will be truncated appropriately.

        The interval must have finite diameter.
        """
        if self.diameter == _INF:
            raise ValueError("cannot subdivide an infinite interval")
        if subdivisions < 1:
            raise ValueError("number of subdivisions must be 1 or greater")
        subdivision_width = self.diameter / subdivisions
        counter = 1
        subdivision = self.lower_bound
        while subdivision <= self.upper_bound:
            yield subdivision
            subdivision = self.lower_bound + counter * subdivision_width
            counter += 1

    def intersects(self, other: Interval) -> bool:
        """
        ### Description
        Returns `True` if there are any values present in both intervals.
        """
        return (
            other.lower_bound <= self.upper_bound
            and self.lower_bound <= other.upper_bound
        )

    # ----------------------------------- MANIPULATE --------------------------------- #

    def change_width(self, amount: Number) -> Interval:
        """
        ### Description
        Expands or contracts the interval depending whether the `amount` specified is a
        positive or negative number.
        """
        return Interval(
            self.lower_bound - amount,
            self.upper_bound + amount,
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def truncate(self, precision: int) -> Interval:
        """
        ### Description
        Rounds the lower bound down and the upper bound up, to the provided precision.
        """
        # Negative precisions round to increasing powers of 10;
        # 0 precision is meaningless.
        if precision == 0:
            raise ValueError("precision cannot be exactly equal to 0")

        # floor and ceil with precision argument
        def _floor(_x: Number, _p: int) -> float:
            return float(round(_x - 0.5 * 10**-_p, _p))

        def _ceil(_x: Number, _p: int) -> float:
            return float(round(_x + 0.5 * 10**-_p, _p))

        return Interval(
            _floor(self.lower_bound, _p=precision),
            _ceil(self.upper_bound, _p=precision),
            upper_closure="open",
        )

    # -------------------------------- HELPER METHODS -------------------------------- #

    @staticmethod
    def _invert(it: IntervalType) -> IntervalType:
        if it == "closed":
            return "open"
        return "closed"

    @staticmethod
    def _x_div_0_is_inf(
        x: Number, y: Number, fn: Callable[[Number, Number], Number]
    ) -> Number:
        """
        A private staticmethod. Handles floor and true division by zero as INF or -INF.
        """

        try:
            return fn(x, y)
        except ZeroDivisionError:
            return _INF * copysign(1, x)

    ####################################### MATH #######################################

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interval):
            return NotImplemented
        return (
            self.lower_bound,
            self.upper_bound,
            self.lower_closure,
            self.upper_closure,
        ) == (
            other.lower_bound,
            other.upper_bound,
            other.lower_closure,
            other.upper_closure,
        )

    # ---------------------------------- COMPARISON ---------------------------------- #

    # NOTE that between two Intervals, >= and > are the same, and <= and < are the same.

    @staticmethod
    def _triangle_area(x: float) -> float:
        """
        Area of a right isosceles triangle with base and height x, or 0 if area would be
        less than zero.
        """
        return x**2 / 2 if x > 0 else 0

    def __lt__(self, other: Interval) -> bool | float:
        def _lt_helper(interval: Interval, value: Number) -> bool | float:
            def _invlerp(interval: Interval, value: Number) -> Number:
                return (value - interval.adjusted_lower_bound) / interval.diameter

            if value in interval:
                return _invlerp(interval, value)
            if value >= interval.lower_bound:
                return True
            return False

        if isinstance(self, (float, int)):
            out = _lt_helper(other, self)
        elif self.diameter == 0:
            out = _lt_helper(other, self.lower_bound)
        if isinstance(other, (float, int)):
            out = _lt_helper(self, other)
        elif other.diameter == 0:
            out = _lt_helper(self, other.lower_bound)

        else:
            out = (
                0
                + Interval._triangle_area(other.upper_bound - self.lower_bound)
                - Interval._triangle_area(other.lower_bound - self.lower_bound)
                - Interval._triangle_area(other.upper_bound - self.upper_bound)
                + Interval._triangle_area(other.lower_bound - self.upper_bound)
            ) / (self.diameter * other.diameter)

        if 0 < out < 1:
            return out
        return bool(out)

    def __le__(self, _: Any) -> NotImplementedType:
        return NotImplemented

    def __gt__(self, other: Interval) -> bool | float:
        out = 1 - (self < other)
        if 0 < out < 1:
            return out
        return bool(out)

    def __ge__(self, _: Any) -> NotImplementedType:
        return NotImplemented

    def __invert__(self) -> Interval:
        return Interval(
            self.lower_bound,
            self.upper_bound,
            lower_closure=Interval._invert(self.lower_closure),
            upper_closure=Interval._invert(self.upper_closure),
        )

    def __neg__(self) -> Interval:
        return Interval(
            -self.lower_bound,
            -self.upper_bound,
            lower_closure=Interval._invert(self.lower_closure),
            upper_closure=Interval._invert(self.upper_closure),
        )

    def __contains__(self, value: Number) -> bool:
        return self.adjusted_lower_bound <= value <= self.adjusted_upper_bound

    def __add__(self, value: Number) -> Interval:
        return Interval(
            self.lower_bound + value,
            self.upper_bound + value,
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    __radd__ = __add__

    def __sub__(self, value: Number) -> Interval:
        return Interval(
            self.lower_bound - value,
            self.upper_bound - value,
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    __rsub__ = __sub__

    def __mul__(self, value: Number) -> Interval:
        return Interval(
            self.lower_bound * value,
            self.upper_bound * value,
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    __rmul__ = __mul__

    def __truediv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(self.lower_bound, value, op.truediv),
            Interval._x_div_0_is_inf(self.upper_bound, value, op.truediv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __rtruediv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(value, self.lower_bound, op.truediv),
            Interval._x_div_0_is_inf(value, self.upper_bound, op.truediv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __floordiv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(self.lower_bound, value, op.floordiv),
            Interval._x_div_0_is_inf(self.upper_bound, value, op.floordiv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __rfloordiv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(value, self.upper_bound, op.floordiv),
            Interval._x_div_0_is_inf(value, self.lower_bound, op.floordiv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __and__(self, other: Interval) -> Interval:
        if not self.intersects(other):
            return EMPTY_SET
        return Interval(
            max(self.lower_bound, other.lower_bound),
            min(self.upper_bound, other.upper_bound),
        )

    def __or__(self, other: Interval) -> Interval:
        if not self.intersects(other):
            raise ValueError(
                "intervals must intersect or be adjacent to create a union"
            )
        min_lower_bounded: Interval = (
            self if self.lower_bound < other.lower_bound else other
        )
        max_upper_bounded: Interval = (
            self if self.upper_bound > other.upper_bound else other
        )
        return Interval(
            min(self.lower_bound, other.lower_bound),
            max(self.upper_bound, other.upper_bound),
            lower_closure=min_lower_bounded.lower_closure,
            upper_closure=max_upper_bounded.upper_closure,
        )

    def __str__(self) -> str:
        if self.diameter == 0:
            return "∅"
        if self.lower_bound == self.upper_bound:
            return str(self.lower_bound)
        s, e = self.lower_bound, self.upper_bound
        l_bracket = "[" if self.lower_closure == "closed" else "("
        r_bracket = "]" if self.upper_closure == "closed" else ")"
        return f"{l_bracket}{s}, {e}{r_bracket}"

    def __repr__(self) -> str:
        lo, hi = self.lower_bound, self.upper_bound
        loc = self.lower_closure
        hic = self.upper_closure
        return (
            f"Interval("
            f"lower_bound={lo}, upper_bound={hi}, "
            f"lower_closure={loc}, upper_closure={hic}"
            f")"
        )


EMPTY_SET: Interval = Interval(0, 0, lower_closure="open", upper_closure="open")
