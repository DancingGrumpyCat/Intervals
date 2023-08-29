########################################################################################
#                                        IMPORTS                                       #
########################################################################################

from __future__ import annotations

import fractions
import math
import operator as op
import random
import warnings
from enum import Enum
from functools import reduce
from typing import TYPE_CHECKING, Any, Literal, Sequence, Union, cast, get_args

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

########################################################################################
#                                       CONSTANTS                                      #
########################################################################################


Number = Union[int, float, fractions.Fraction]
"""A type alias for the `float | int | Fraction` union."""

EPSILON: float = 1e-15
_INF: float = float("inf")


class IntervalError(Exception):
    def __init__(
        self, msg1: str, msg2: str | None = None, msg3: str | None = None, /
    ) -> None:
        """
        ### Example:
        "{number to union with interval} must be {adjacent to or within interval}
        ({other} not adjacent to or within {self})"
        """

        if not (msg2 is None or msg3 is None):
            super().__init__(f"{msg1} must be {msg2} ({msg3})")
        else:
            super().__init__(msg1)


class IntervalValueError(IntervalError):
    pass


class IntervalTypeError(IntervalError):
    pass


class IntervalType(Enum):
    OPEN = "open"
    """A single open bound, or an interval where both bounds are open."""
    CLOSED = "closed"
    """A single closed bound, or an interval where both bounds are closed."""
    HALF_OPEN = "half-open"
    """An interval where one bound is closed and the other is open, in either order."""


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

        # Put start & end in the right order
        if self.lower_bound > self.upper_bound:
            self.lower_bound, self.upper_bound = (
                self.upper_bound,
                self.lower_bound,
            )
            self.lower_closure, self.upper_closure = (
                self.upper_closure,
                self.lower_closure,
            )

        # The actual values of the bounds adjusted by a tiny number
        # TODO: this number's magnitude should depend somehow on the magnitude of the
        # interval's bounds
        self.adjusted_lower_bound: Number = self.lower_bound + EPSILON * (
            self.lower_closure == IntervalType.OPEN
        )
        self.adjusted_upper_bound: Number = self.upper_bound - EPSILON * (
            self.upper_closure == IntervalType.OPEN
        )


########################################################################################
#                                      MAIN CLASS                                      #
########################################################################################


class Interval:
    """
    ### Description
    An Interval is a connected subset of ℝ. It must always have a lower and upper bound,
    as well as two values indicating closed/open state for each bound. Each bound may be
    infinite&mdash;some methods not being available if they are.

    ### Initialization
    To use the basic `__init__`, write:

    ```py
    Interval()      # {0}
    Interval(y)     # [0, y)
    Interval(x, y)  # [x, y)
    ```

    If `x > y`, `y` is swapped with `x`.

    The method `Interval.from_string` allows you to instead initialize from a variety of
    patterns:
    ```py
    Interval.from_string("[-2, 6.1]")  # [-2.0, 6.1]
    Interval.from_string("[ , 0]")     # [-inf, 0.0]
    Interval.from_string("[0, ]")      # [0.0, +inf]
    Interval.from_string("3 +- 2")     # [1.0, 5.0)
    ```

    ### Types
    The arguments with type Number can be integers, floats, or fractions.
    """

    ####################################### INIT #######################################

    def __init__(
        self,
        bound1: Number = 0,
        bound2: Number | None = None,
        /,
        *,
        lower_closure: IntervalType = IntervalType.CLOSED,
        upper_closure: IntervalType = IntervalType.OPEN,
    ) -> None:
        # Initialize bounds
        if bound2 is None:
            bound2, bound1 = bound1, 0
        bounds = Bounds(
            lower_bound=bound1,
            upper_bound=bound2,
            lower_closure=lower_closure,
            upper_closure=upper_closure,
        )

        # The user-facing values of the bounds
        self.lower_bound = bounds.lower_bound
        self.upper_bound = bounds.upper_bound

        # Lower and upper bound interval type (unbounded sides must be closed)
        # Interval type here is either closed or open
        self.lower_closure = bounds.lower_closure
        self.upper_closure = bounds.upper_closure

        self.adjusted_lower_bound = bounds.adjusted_lower_bound
        self.adjusted_upper_bound = bounds.adjusted_upper_bound

        self.datatypes = (type(self.lower_bound), type(self.upper_bound))

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
            lower_closure = (
                IntervalType.OPEN
                if interval_string.startswith("(")
                else IntervalType.CLOSED
            )
            upper_closure = (
                IntervalType.OPEN
                if interval_string.endswith(")")
                else IntervalType.CLOSED
            )
            # convert to canonical form
            interval_string = (
                interval_string.strip("[()]").replace("...", ",").replace("..", ",")
            )
            (lower_bound, upper_bound) = interval_string.split(",")

            try:
                return cls(
                    # default value triggers if string is empty
                    float(lower_bound or -_INF),
                    float(upper_bound or +_INF),
                    lower_closure=lower_closure,
                    upper_closure=upper_closure,
                )
            except ValueError:
                # each bound must be either a float ... or an empty string
                raise IntervalValueError(
                    "each bound",
                    "either a float as a string, or an empty string",
                    f"input was '{original}'",
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

        # interval string must be a valid interval, matching ...(input was ...)
        raise IntervalValueError(
            "interval string",
            "a valid interval, matching either the plus minus form or bracket "
            "notation",
            f"input was '{original}'",
        )

    @classmethod
    def p_adic(
        cls,
        j: int,
        n: int,
        /,
        *,
        p: int = 2,
        lower_closure: IntervalType = IntervalType.CLOSED,
        upper_closure: IntervalType = IntervalType.OPEN,
    ) -> Interval:
        """
        ### Description
        A special type of interval. The input constraints of dyadic intervals force them
        to be structured as a sort of infinite n-ary tree. See
        [Wikipedia: Dyadic Intervals](https://en.wikipedia.org/wiki/Interval_(mathematics)#Dyadic_intervals)
        for the source of this and for more information.

        Useful for quad-trees.

        #### Constraints:
        - `p` should be prime, but since this is a slow test it is not enforced
        - `j` and `n` should be constrained to integers, but for the sake of flexibility
        this is also not enforced

        ### Properties
        If both constraints are followed:
        - width is always an integer power of `p`
        - contained in exactly one p-adic interval of `p` times its length
        - spanned by exactly `p` p-adic intervals of its length over `p`
        - if two open dyadic (`p == 2`) intervals intersect, then one is a subset of
        the other
        """
        return cls(
            j / p**n,
            (j + 1) / p**n,
            lower_closure=lower_closure,
            upper_closure=upper_closure,
        )

    @classmethod
    def approximate(cls, value: float | int, scale: float = 1.0) -> Interval:
        error_bars = math.log2(abs(value) + 1) + 1
        plusminus = scale * error_bars
        return cls(value - plusminus, value + plusminus)

    def where(
        self,
        lower_bound: Number | None = None,
        upper_bound: Number | None = None,
        lower_closure: IntervalType | None = None,
        upper_closure: IntervalType | None = None,
    ) -> Interval:
        if lower_bound is None:
            lower_bound = self.lower_bound
        if upper_bound is None:
            upper_bound = self.upper_bound
        if lower_closure is None:
            lower_closure = self.lower_closure
        if upper_closure is None:
            upper_closure = self.upper_closure
        return Interval(
            lower_bound,
            upper_bound,
            lower_closure=lower_closure,
            upper_closure=upper_closure,
        )

    #################################### PROPERTIES ####################################

    @property
    def absolute_value(self) -> Interval:
        return self if (self > 0) > 0.5 else -self

    @property
    def is_bounded(self) -> bool:
        return _INF not in (abs(self.lower_bound), abs(self.upper_bound))

    @property
    def lower_bound_is_finite(self) -> bool:
        return self.lower_bound != -_INF

    @property
    def upper_bound_is_finite(self) -> bool:
        return self.upper_bound != +_INF

    @property
    def width(self) -> Number:
        """
        ### Description
        The positive difference between the apparent lower and upper bounds.
        """
        return self.upper_bound - self.lower_bound

    @property
    def interval_type(self) -> IntervalType:
        if self.lower_closure == self.upper_closure == IntervalType.CLOSED:
            return IntervalType.CLOSED
        if self.lower_closure == self.upper_closure == IntervalType.OPEN:
            return IntervalType.OPEN
        return IntervalType.HALF_OPEN

    @property
    def midpoint(self) -> Number:
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

    def step(self, step: Number, /, *, start: Number | None = None) -> Iterator[Number]:
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

        original_start: Number | None = start
        if step == 0:
            # step must be nonzero
            raise IntervalValueError("step", "nonzero", f"was {step}")
        if abs(step) == _INF:
            # step must be finite
            raise IntervalValueError("step", "finite", f"was {step}")

        if not (self.lower_bound_is_finite or start is not None):
            start = self.upper_bound

        if not (self.lower_bound_is_finite or self.upper_bound_is_finite):
            # at least one bound must be finite
            raise IntervalValueError(
                "at least one bound", "finite", f"interval was {self}"
            )

        if not (self.lower_bound_is_finite or step <= 0):
            # step must be negative if the lower bound is infinite
            raise IntervalValueError(
                "step", "negative if the lower bound is infinite", f"was {step}"
            )

        if start is None:
            start = self.lower_bound

        if start not in self:
            start += step
            if start not in self:
                # start must be one or fewer steps away from interval
                raise IntervalValueError(
                    "start",
                    "one or fewer steps away from interval",
                    f"interval was {self}, step was {step},"
                    f"and start was {original_start}",
                )
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
        if self.width == _INF:
            raise IntervalValueError(
                "interval to subdivide",
                "finite",
                f"width of {self} is {self.width}",
            )
        if subdivisions < 1:
            raise IntervalValueError(
                "number of subdivisions", "1 or greater", f"was {subdivisions}"
            )
        subdivision_width = self.width / subdivisions
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

    def is_adjacent(self, other: Interval) -> bool:
        """
        ### Description
        Returns `True` if the intervals do not intersect and there are no values between
        them.
        """
        if self.intersects(other):
            return False
        if (
            self.upper_bound == other.lower_bound
            or other.upper_bound == self.lower_bound
        ):
            return True
        return False

    # ----------------------------------- MANIPULATE --------------------------------- #

    def change_width(self, amount: Number) -> Interval:
        """
        ### Description
        Expands or contracts the interval depending whether the `amount` specified is a
        positive or negative number.
        """
        return self.where(
            lower_bound=self.lower_bound - amount,
            upper_bound=self.upper_bound + amount,
        )

    def split(self, value: Number) -> tuple[Interval, Interval, Interval]:
        if value not in self:
            raise IntervalValueError(
                "value", "within interval", f"{value} not in {self}"
            )
        return (
            self.where(upper_bound=value, upper_closure=IntervalType.OPEN),
            Interval(value, value),
            self.where(lower_bound=value, lower_closure=IntervalType.CLOSED),
        )

    def closed(self) -> Interval:
        return self.where(
            lower_closure=IntervalType.CLOSED,
            upper_closure=IntervalType.CLOSED,
        )

    def opened(self) -> Interval:
        return self.where(
            lower_closure=IntervalType.OPEN,
            upper_closure=IntervalType.OPEN,
        )

    # -------------------------------- HELPER METHODS -------------------------------- #

    @staticmethod
    def _invert(it: IntervalType) -> IntervalType:
        if it == IntervalType.CLOSED:
            return IntervalType.OPEN
        return IntervalType.CLOSED

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
        return not (self.interval_type == IntervalType.OPEN and self.width == 0)

    def __len__(self) -> int:
        return math.floor(self.adjusted_upper_bound) - math.floor(
            self.adjusted_lower_bound
        )

    def __iter__(self) -> Iterator[Number]:
        sign = +1
        if self.lower_bound == -_INF:
            if self.upper_bound == _INF:
                raise IntervalValueError(
                    "interval to iterate in",
                    "bounded in at least one direction",
                    f"was {self}",
                )
            sign = -1
        yield from self.step(sign)

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
    # First, draw A on the x axis and B on the y axis. There is a rectangle `mnop` where
    # they intersect. Let's call it AxB.The line y = x bounds ShadedArea below. Triangle
    # `jkn`----where ShadedArea intersects AxB----fills some proportion of AxB.
    #
    # That proportion is the probability we seek. We can calculate that by starting with
    # triangle `pli`, and by subtracting both triangles `olk` and `mji` (right isosceles
    # triangles----the points `i`, `j`, `k`, and `l` all lie on y=x.
    #
    # We calculate the areas of the triangles as 0 if they're negative, so that we don't
    # subtract when we don't want to. We then add back triangle `jkn` if necessary, with
    # the same technique if its area is negative.
    #
    #
    # Link: https://www.desmos.com/calculator/iusjba8eis
    #
    # --------------------------------------|
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
    # --------------------------------------|

    @staticmethod
    def _triangle_area(x: Number) -> Number:
        """
        Area of a right isosceles triangle with base and height x, or 0 if area would be
        less than zero.
        """
        return x**2 / 2 if x > 0 else 0

    def __lt__(self, other: object) -> bool | Number:
        if not isinstance(other, (Interval, float, int)):
            return NotImplemented

        def _lt_helper(interval: Interval, value: Number) -> bool | Number:
            if value in interval:
                return invlerp(interval, value)
            return value >= interval.lower_bound

        out: bool | Number
        if self.width == 0:
            if not isinstance(other, Interval):
                return NotImplemented
            out = _lt_helper(interval=other, value=self.lower_bound)
        elif isinstance(other, (float, int)):
            out = _lt_helper(interval=self, value=other)
        elif other.width == 0:
            out = _lt_helper(interval=self, value=other.lower_bound)

        else:
            # fmt: off
            out = (
                + Interval._triangle_area(other.upper_bound - self.lower_bound)
                - Interval._triangle_area(other.lower_bound - self.lower_bound)
                - Interval._triangle_area(other.upper_bound - self.upper_bound)
                + Interval._triangle_area(other.lower_bound - self.upper_bound)
            ) / (self.width * other.width)
            # fmt: on

        if 0 < out < 1:
            return out
        return bool(out)

    def __gt__(self, other: object) -> bool | Number:
        out = 1 - (self < other)
        if 0 < out < 1:
            return out
        return bool(out)

    def __le__(self, other: object) -> bool | Number:
        warnings.warn(
            "A <= B is the same as A < B between intervals and intervals, and between "
            "intervals and numbers. Use < instead.",
            SyntaxWarning,
            stacklevel=2,
        )
        return self < other

    def __ge__(self, other: object) -> bool | Number:
        warnings.warn(
            "A >= B is the same as A > B between intervals and intervals, and between "
            "intervals and numbers. Use > instead.",
            SyntaxWarning,
            stacklevel=2,
        )
        return self > other

    def __invert__(self) -> Interval:
        return self.where(
            lower_closure=Interval._invert(self.lower_closure),
            upper_closure=Interval._invert(self.upper_closure),
        )

    def __neg__(self) -> Interval:
        return self.where(
            lower_bound=-self.lower_bound,
            upper_bound=-self.upper_bound,
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

    @staticmethod
    def _fmt_dunder_type_error(p1: Any, p2: Any) -> tuple[str, str, str]:
        return (
            "input",
            "Interval and Number, or Interval and Interval",
            f"was {p1} ({type(p1).__name__}) + {p2} ({type(p2).__name__})",
        )

    def __add__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return self.where(
                lower_bound=self.lower_bound + other,
                upper_bound=self.upper_bound + other,
            )

        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, op.add)

        raise IntervalTypeError(*Interval._fmt_dunder_type_error(self, other))

    __radd__ = __add__

    def __sub__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return self.where(
                lower_bound=self.lower_bound - other,
                upper_bound=self.upper_bound - other,
            )

        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, op.sub)

        raise IntervalTypeError(*Interval._fmt_dunder_type_error(self, other))

    __rsub__ = __sub__

    def __mul__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return self.where(
                lower_bound=self.lower_bound * other,
                upper_bound=self.upper_bound * other,
            )

        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, op.mul)

        raise IntervalTypeError(*Interval._fmt_dunder_type_error(self, other))

    __rmul__ = __mul__

    def __truediv__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return self.where(
                lower_bound=self.lower_bound / other,
                upper_bound=self.upper_bound / other,
            )

        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, op.truediv)

        raise IntervalTypeError(*Interval._fmt_dunder_type_error(self, other))

    def __rtruediv__(self, value: Number) -> Interval:
        return self.where(
            lower_bound=Interval._x_div_0_is_inf(value, self.lower_bound, op.truediv),
            upper_bound=Interval._x_div_0_is_inf(value, self.upper_bound, op.truediv),
        )

    def __floordiv__(self, other: Number | Interval) -> Interval:
        if isinstance(other, (float, int)):
            return self.where(
                lower_bound=self.lower_bound // other,
                upper_bound=self.upper_bound // other,
            )

        if isinstance(other, Interval):
            return Interval._binary_fn(self, other, op.floordiv)

        raise IntervalTypeError(*Interval._fmt_dunder_type_error(self, other))

    def __rfloordiv__(self, value: Number) -> Interval:
        return self.where(
            lower_bound=Interval._x_div_0_is_inf(value, self.lower_bound, op.floordiv),
            upper_bound=Interval._x_div_0_is_inf(value, self.upper_bound, op.floordiv),
        )

    def __pow__(self, exponent: Number) -> Interval:
        if not (
            isinstance(exponent, int)
            or (self.lower_bound >= 0 and self.upper_bound >= 0)
        ):
            raise IntervalTypeError(
                "exponent",
                "an integer if either bound is negative",
                f"input was {self} ** {exponent}",
            )
        return self.where(
            lower_bound=self.lower_bound**exponent,
            upper_bound=self.upper_bound**exponent,
        )

    def __rmod__(self, value: Number) -> Number:
        if not isinstance(value, (float, int)):
            raise IntervalTypeError(
                "value",
                "of type `Number` (int | float)",
                f"was {value} ({type(value).__name__})",
            )
        return value % self.width + self.lower_bound

    def __and__(self, other: Interval) -> Interval:
        if not self.intersects(other):
            return EMPTY_SET
        return Interval(
            max(self.lower_bound, other.lower_bound),
            min(self.upper_bound, other.upper_bound),
        )

    # union
    def __or__(self, other: Number | Interval) -> Interval:
        if not isinstance(other, (*get_args(Number), Interval)):
            return NotImplemented

        # without this, mypy gets confused about get_args
        other = cast("Interval | Number", other)  # type: ignore[redundant-cast]

        # if other is Interval
        if isinstance(other, Interval):
            if not (self.intersects(other) or self.is_adjacent(other)):
                raise IntervalValueError(
                    "intervals must intersect or be adjacent to create a union"
                )
            return Interval(
                min(self.lower_bound, other.lower_bound),
                max(self.upper_bound, other.upper_bound),
                # lower closure of the interval with the lower lower bound, and
                # upper closure of the interval with the higher upper bound
                lower_closure=(
                    self if self.lower_bound < other.lower_bound else other
                ).lower_closure,
                upper_closure=(
                    self if self.upper_bound > other.upper_bound else other
                ).upper_closure,
            )

        # if other is a Number, and also within the interval, just return the number
        if other in self.closed():
            return self
        # if other is a Number, but not within the interval, raise a ValueError
        raise IntervalValueError(
            "value",
            "adjacent to or within interval",
            f"{other} neither adjacent to nor within {self}",
        )

    def __ror__(self, value: Number) -> Interval:
        if value == self.lower_bound:
            return self.where(lower_closure=IntervalType.CLOSED)
        if value == self.upper_bound:
            return self.where(upper_closure=IntervalType.CLOSED)
        if value in self:
            return self
        raise IntervalValueError(
            "value",
            "adjacent to or within interval",
            f"{value} neither adjacent to nor within {self}",
        )

    @staticmethod
    def _round(x: Number, ndigits: int, direction: Literal[-1, 1]) -> Number:
        """
        ### Description
        Rounds x down (floor) or up (ceil) if direction is +1 or -1 respectively. Errors
        if direction has any other value. Also takes ndigits: the precision to round to.
        """
        if float(x).is_integer():
            return x
        if abs(direction) != 1:
            raise IntervalValueError(
                "direction", "up (+1) or down (-1)", f"was {direction}"
            )
        out = round(x + direction * (0.5 * 10**-ndigits), ndigits)
        return float(out) if ndigits > 0 else int(out)

    def __round__(self, ndigits: int | None = None) -> Interval:
        """
        ### Description
        Rounds the lower bound down and the upper bound up, to the provided ndigits.

        Negative precision rounds to increasing powers of 10.
        """

        # Make integers if ndigits is None or 0
        # (Must be None and not 0 because of the previous check)
        if not ndigits:
            return self.where(
                lower_bound=math.floor(self.lower_bound),
                upper_bound=math.ceil(self.upper_bound),
            )

        return self.where(
            lower_bound=Interval._round(
                self.lower_bound, ndigits=ndigits, direction=-1
            ),
            upper_bound=Interval._round(self.upper_bound, ndigits=ndigits, direction=1),
        )

    def __floor__(self, ndigits: int = 0) -> Interval:
        return Interval(
            Interval._round(self.lower_bound, ndigits=ndigits, direction=-1),
            Interval._round(self.upper_bound, ndigits=ndigits, direction=-1),
            lower_closure=IntervalType.OPEN,
            upper_closure=IntervalType.CLOSED,
        )

    def __ceil__(self, ndigits: int = 0) -> Interval:
        return Interval(
            Interval._round(self.lower_bound, ndigits=ndigits, direction=1),
            Interval._round(self.upper_bound, ndigits=ndigits, direction=1),
            lower_closure=IntervalType.OPEN,
            upper_closure=IntervalType.CLOSED,
        )

    def __str__(self) -> str:
        # Empty set
        if self.width == 0 and self.interval_type == IntervalType.OPEN:
            return "{∅}"

        # Degenerate interval
        if self.lower_bound == self.upper_bound:
            return str(self.lower_bound).join("{}")

        # Normal
        lower, upper = self.lower_bound, self.upper_bound
        l_bracket = "[" if self.lower_closure == IntervalType.CLOSED else "("
        r_bracket = "]" if self.upper_closure == IntervalType.CLOSED else ")"
        return f"{l_bracket}{lower}, {upper}{r_bracket}"

    def __repr__(self) -> str:
        lo, hi = self.lower_bound, self.upper_bound
        loc = self.lower_closure.name
        hic = self.upper_closure.name
        return (
            f"Interval("
            f"lower_bound={lo}, upper_bound={hi}, "
            f"lower_closure={loc}, upper_closure={hic}"
            f")"
        )


########################################################################################
#                                  INTERVAL CONSTANTS                                  #
########################################################################################


EMPTY_SET: Interval = Interval(0).opened()
UNIT = Interval(1)
UNIT_DISK = (-UNIT | UNIT).closed()
POSITIVE_REALS = Interval(float("inf")).closed()
NATURALS: Iterator[int] = (int(x) for x in (POSITIVE_REALS).step(1))
WHOLE_NUMBERS: Iterator[int] = (int(x) for x in (POSITIVE_REALS + 1).step(1))
PI = Interval.from_string(f"({223 / 71}, {22 / 7})")


########################################################################################
#                                   UTILITY FUNCTIONS                                  #
########################################################################################

###################################### REDUCTIONS ######################################


def union(intervals: Sequence[Interval]) -> Interval:
    """
    Returns the union-reduction of a sequence of intervals; that is, it starts with the
    degenerate interval {0}, and progressively unions each interval in the sequence from
    left to right.
    """
    return reduce(lambda x, y: x | y, intervals)


######################################### OTHER ########################################


def rand_uniform(interval: Interval, *, values: int = 1) -> list[float]:
    """
    Return a random float within finite interval.
    """
    if abs(interval.adjusted_lower_bound) == float("inf") or abs(
        interval.upper_bound
    ) == float("inf"):
        raise IntervalValueError("bounds of interval", "finite", f"was {interval})")

    def _random(interval: Interval) -> float:
        return random.random() * interval.width + interval.lower_bound

    return [_random(interval) for _ in range(values)]


def rand_interval(
    lower_bound_interval: Interval, upper_bound_interval: Interval
) -> Interval:
    return Interval(
        rand_uniform(lower_bound_interval)[0],
        rand_uniform(upper_bound_interval)[0],
    )


def lerp(interval: Interval, t: Number) -> Number:
    return interval.adjusted_lower_bound + t * interval.width


def invlerp(interval: Interval, value: Number) -> Number:
    return (value - interval.adjusted_lower_bound) / interval.width


def remap(interval1: Interval, interval2: Interval, value: Number) -> Number:
    t: Number = invlerp(interval1, value)
    return lerp(interval2, t)


def clamp(value: Number, interval: Interval) -> Number:
    """
    Clamp value to within interval.
    """
    if interval.width == 0:
        if interval.lower_closure == interval.upper_closure == IntervalType.OPEN:
            raise IntervalValueError("interval", "not the empty set", f"was {interval}")
        return interval.lower_bound
    return min(interval.upper_bound, max(interval.lower_bound, value))


def boltzmann(a: Number, xs: Sequence[Number], /, *, base: Number = math.e) -> Number:
    """
    ### Description
    Returns the min, mean, or max of a sequence of numbers depending if a is -inf, 0, or
    +inf. If a is none of those, the result is a smoothed min or max. The result of this
    is differentiable over the input parameters.

    Only change the base parameter if you know what you're doing.
    """
    return sum(x * base ** (a * x) for x in xs) / sum(base ** (a * x) for x in xs)


def smooth_clamp(value: Number, interval: Interval, a: Number) -> Number:
    """
    ### Description
    Uses the Boltzmann operator to differentiably clamp to an interval.
    """

    return boltzmann(
        -a, (interval.upper_bound, boltzmann(a, (interval.lower_bound, value)))
    )


def antipode(value: Number, interval: Interval) -> Number:
    """
    ### Description
    Return the value reflected across the midpoint of the interval
    """
    return interval.midpoint - value
