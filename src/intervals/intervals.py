########################################################################################
#                                        IMPORTS                                       #
########################################################################################

from __future__ import annotations

import math
import operator as op
import warnings
from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator

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
        /,
        *,
        lower_bound: Number = 0,
        upper_bound: Number = 0,
        lower_closure: IntervalType,
        upper_closure: IntervalType,
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
        bound1: Number = 0,
        bound2: Number | None = None,
        /,
        *,
        lower_closure: IntervalType = "open",
        upper_closure: IntervalType = "closed",
    ) -> None:
        # Initialize bounds
        if bound2 is None:
            bound2 = bound1
            bound1 = 0
        bounds = Bounds(
            lower_bound=bound1,
            upper_bound=bound2,
            lower_closure=lower_closure,
            upper_closure=upper_closure,
        )

        # Put start & end in the right order
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
        # Interval type here is either closed or open
        self.lower_closure: IntervalType = (
            "closed" if abs(bounds.lower_bound) == _INF else bounds.lower_closure
        )
        self.upper_closure: IntervalType = (
            "closed" if abs(bounds.upper_bound) == _INF else bounds.upper_closure
        )

        self.adjusted_lower_bound = bounds.adjusted_lower_bound
        self.adjusted_upper_bound = bounds.adjusted_upper_bound

    @classmethod
    def from_string(cls, interval_string: str, /) -> Interval:
        original = interval_string
        interval_string = interval_string.lower().strip().replace(" ", "")

        # Normal form
        if (
            interval_string.startswith(("[", "("))
            and interval_string.endswith((")", "]"))
            and ("," in interval_string or ".." in interval_string)
        ):
            lower_closure: IntervalType = (
                "open" if interval_string.startswith("(") else "closed"
            )
            upper_closure: IntervalType = (
                "open" if interval_string.endswith(")") else "closed"
            )

            interval_string = interval_string.strip("[()]").replace(
                "..", ","
            )  # convert to canonical form
            (lower_bound, upper_bound) = interval_string.split(",")

            try:
                return Interval(
                    # default value triggers if string is empty
                    float(lower_bound or -_INF),
                    float(upper_bound or +_INF),
                    lower_closure=lower_closure,
                    upper_closure=upper_closure,
                )
            except ValueError:
                raise ValueError(
                    f"failed to parse string '{original}' as Interval because one of "
                    f"'{lower_bound}', '{upper_bound}' is either not a float or not an "
                    f"empty string"
                ) from None

        # Plus/Minus form
        if any(
            separator in interval_string
            for separator in ("pm", "p/m", "+-", "+/-", "±")
        ):
            interval_string = (
                interval_string.replace("±", "pm")
                .replace("+-", "pm")
                .replace("+/-", "pm")
                .replace("p/m", "pm")
            )
            center, plusminus = map(float, interval_string.split("pm"))
            return Interval(center - plusminus, center + plusminus)

        raise ValueError(f"failed to parse '{original}' as Interval")

    #################################### PROPERTIES ####################################

    @property
    def is_bounded(self) -> bool:
        return _INF not in (abs(self.lower_bound), abs(self.upper_bound))

    @property
    def lower_bound_is_finite(self) -> bool:
        return self.lower_bound != -_INF

    @property
    def upper_bound_is_finite(self) -> bool:
        return self.lower_bound != +_INF

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

    def step(self, step: float, /, *, start: float | None = None) -> Iterator[float]:
        """
        ### Description
        Returns an iterator that yields values starting from `start` or the lower bound,
        adding `step` each time. Step may be negative. Stops yielding before the values
        exceed the bounds in either direction.

        The function attempts once to step into the interval, if the membership check is
        false beforehand.

        If the lower bound is infinite, start defaults to the upper bound instead, so if
        the upper bound is also infinite, a ValueError is raised.
        """

        if step == 0:
            raise ValueError("step must be non-zero")

        if not self.lower_bound_is_finite:
            if start is None:
                start = self.upper_bound
            if step > 0:
                raise ValueError(
                    "if the lower bound is infinite, step must be negative"
                )
            if not self.upper_bound_is_finite:
                raise ValueError("at least one bound must be finite")

        if start is None:
            start = self.lower_bound

        if start not in self:
            start += step
            if start not in self:
                raise ValueError("start too far away from interval")

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
        is not an integer, the last subdivision will be shortened appropriately.

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
            other.adjusted_lower_bound <= self.adjusted_upper_bound
            and self.adjusted_lower_bound <= other.adjusted_upper_bound
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
            return _INF * math.copysign(1, x)

    ###################################### DUNDERS #####################################

    def __bool__(self) -> bool:
        # Only empty sets will return False
        # Degenerate intervals return True
        return not (self.interval_type == "open" and self.diameter == 0)

    def __len__(self) -> int:
        return math.floor(self.adjusted_upper_bound) - math.floor(
            self.adjusted_lower_bound
        )

    def __iter__(self) -> Generator[Number] | None:
        if self.lower_bound == -_INF:
            yield from self.step(-1)
            if self.upper_bound == _INF:
                raise ValueError(f"cannot iterate over infinite interval {self}")
        if self.upper_bound == _INF:
            yield _INF
        else:
            yield from self.step(1)

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

    def __ne__(self, other: object) -> bool:
        return not self == other

    # ---------------------------------- COMPARISON ---------------------------------- #

    # NOTE that between two Intervals, >= and > are the same, and <= and < are the same.

    # # How to calculate the probability of *A* < *B*.
    # First, draw A and B as independent intervals on the x and y axes. There is a rect-
    # angle where they intersect. Let's call it AxB.The line y = x bounds ShadedArea be-
    # low. The triangle JKN----where ShadedArea intersects AxB----fills some proportion
    # of AxB. That proportion is the probability we seek.
    #
    # We can calculate that by starting with triangle PLI, and subtracting triangles OLK
    # and MJI. They are right isosceles triangles----the points i j k l all lie on y=x.
    #
    # We calculate the areas of the triangles as 0 if they're negative so that we don't
    # subtract when we don't want to. We then add back triangle jkn, calculated the same
    # way (depending on its orientation, it can be 0).
    #
    #
    # Link: https://www.desmos.com/calculator/iusjba8eis
    #
    # ---------------------------------------|
    #      y                                |
    #      ^  --B--   ShadedArea := y < x   |
    #      |                                |
    #      |..b1--b2.../                    |
    #      |..|...|.../                     |
    #      |..|...|../                      |
    #   |  |--p---o-l---a2  |               |
    #   |  |..|...|/        |               |
    #   A  |..|...k         A               |
    #   |  |..|../|         |               |
    #   |  |--m-j-n-----a1  |               |
    #      |..|/  |                         |
    #      |..i   |                         |
    #      | /|   |                         |
    #      0--|---|-------> x               |
    #                                       |
    #         --B--                         |
    # ---------------------------------------|

    @staticmethod
    def _triangle_area(x: float) -> float:
        """
        Area of a right isosceles triangle with base and height x, or 0 if area would be
        less than zero.
        """
        return x**2 / 2 if x > 0 else 0

    def __lt__(self, other: object) -> bool | float:
        if not isinstance(other, (Interval, float, int)):
            return NotImplemented

        def _lt_helper(interval: Interval, value: Number) -> bool | float:
            def _invlerp(interval: Interval, value: Number) -> Number:
                return (value - interval.adjusted_lower_bound) / interval.diameter

            if value in interval:
                return _invlerp(interval, value)
            return value >= interval.lower_bound

        out: bool | float
        if self.diameter == 0:
            if not isinstance(other, Interval):
                return NotImplemented
            out = _lt_helper(interval=other, value=self.lower_bound)
        elif isinstance(other, (float, int)):
            out = _lt_helper(interval=self, value=other)
        elif other.diameter == 0:
            out = _lt_helper(interval=self, value=other.lower_bound)

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

    def __gt__(self, other: object) -> bool | float:
        out = 1 - (self < other)
        if 0 < out < 1:
            return out
        return bool(out)

    def __le__(self, other: object) -> bool | float:
        warnings.warn(
            "A <= B is the same as A < B between intervals and intervals, and between "
            "intervals and numbers. Use < instead.",
            SyntaxWarning,
            stacklevel=2,
        )
        return self < other

    def __ge__(self, other: object) -> bool | float:
        warnings.warn(
            "A >= B is the same as A > B between intervals and intervals, and between "
            "intervals and numbers. Use > instead.",
            SyntaxWarning,
            stacklevel=2,
        )
        return self > other

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
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __pos__(self) -> Interval:
        return self

    def __contains__(self, value: Number) -> bool:
        return self.adjusted_lower_bound <= value <= self.adjusted_upper_bound

    @staticmethod
    def _binary_fn(
        x: Interval, y: Interval, fn: Callable[[Number, Number], Number]
    ) -> Interval:
        possible_bounds: list[Number] = [
            fn(x.lower_bound, y.lower_bound),
            fn(x.lower_bound, y.upper_bound),
            fn(x.upper_bound, y.lower_bound),
            fn(x.upper_bound, y.upper_bound),
        ]
        return Interval(
            min(possible_bounds),
            max(possible_bounds),
        )

    def __add__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return Interval(
                self.lower_bound + other,
                self.upper_bound + other,
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )
        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, lambda x, y: x + y)
        raise TypeError("input must be Interval and Number, or Interval and Interval")

    __radd__ = __add__

    def __sub__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return Interval(
                self.lower_bound - other,
                self.upper_bound - other,
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )
        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, lambda x, y: x - y)
        raise TypeError("input must be Interval and Number, or Interval and Interval")

    __rsub__ = __sub__

    def __mul__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return Interval(
                self.lower_bound * other,
                self.upper_bound * other,
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )
        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, lambda x, y: x * y)
        raise TypeError("input must be Interval and Number, or Interval and Interval")

    __rmul__ = __mul__

    def __truediv__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return Interval(
                self.lower_bound / other,
                self.upper_bound / other,
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )
        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, lambda x, y: x / y)
        raise TypeError("input must be Interval and Number, or Interval and Interval")

    def __rtruediv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(value, self.lower_bound, op.truediv),
            Interval._x_div_0_is_inf(value, self.upper_bound, op.truediv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __floordiv__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return Interval(
                self.lower_bound // other,
                self.upper_bound // other,
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )
        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, lambda x, y: x // y)
        raise TypeError("input must be Interval and Number, or Interval and Interval")

    def __rfloordiv__(self, value: Number) -> Interval:
        return Interval(
            Interval._x_div_0_is_inf(value, self.upper_bound, op.floordiv),
            Interval._x_div_0_is_inf(value, self.lower_bound, op.floordiv),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __pow__(self, exponent: int) -> Interval:
        if not isinstance(exponent, int):
            raise TypeError("exponent must be an integer")
        return Interval(
            self.lower_bound**exponent,
            self.upper_bound**exponent,
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

    # union
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

    # floor or ceil with precision and direction arguments
    def _round(_x: Number, _p: int, _direction: int) -> Number:
        if _direction not in (-1, +1):
            raise ValueError("direction must be up (+1) or down (-1)")
        out = round(_x + _direction * (0.5 * 10**-_p), _p)
        return float(out) if _p > 0 else int(out)

    def __round__(self, ndigits: int | None = None) -> Interval:
        """
        ### Description
        Rounds the lower bound down and the upper bound up, to the provided ndigits.

        Negative precision round to increasing powers of 10.
        """

        # Make integers if ndigits is None or 0
        # (Must be None and not 0 because of the previous check)
        if not ndigits:
            return Interval(
                math.floor(self.lower_bound),
                math.ceil(self.upper_bound),
                lower_closure=self.lower_closure,
                upper_closure=self.upper_closure,
            )

        return Interval(
            Interval._round(self.lower_bound, _p=ndigits, _direction=-1),
            Interval._round(self.upper_bound, _p=ndigits, _direction=+1),
            lower_closure=self.lower_closure,
            upper_closure=self.upper_closure,
        )

    def __floor__(self, ndigits: int = 0) -> Interval:
        return Interval(
            Interval._round(self.lower_bound, _p=ndigits, _direction=-1),
            Interval._round(self.upper_bound, _p=ndigits, _direction=-1),
            lower_closure="open",
            upper_closure="closed",
        )

    def __ceil__(self, ndigits: int = 0) -> Interval:
        return Interval(
            Interval._round(self.lower_bound, _p=ndigits, _direction=+1),
            Interval._round(self.upper_bound, _p=ndigits, _direction=+1),
            lower_closure="open",
            upper_closure="closed",
        )

    def __str__(self) -> str:
        if self.diameter == 0 and self.interval_type == "open":
            return "{∅}"
        if self.lower_bound == self.upper_bound:
            return str(self.lower_bound).join("{}")
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
