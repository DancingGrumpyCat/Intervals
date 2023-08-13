import random
from typing import Callable

from intervals.intervals import Interval, Number


def clamp(value: Number, interval: Interval) -> Number:
    """
    Clamp value to within interval.
    """
    if interval.diameter == 0:
        raise ValueError("Magnitude of interval must be non-zero.")
    if interval.diameter < 0:
        raise ValueError(
            "I have no idea how you got this error."
            "Magnitude should always be non-negative."
        )
    return min(interval.adjusted_upper_bound, max(interval.adjusted_lower_bound, value))


def binary_fn(
    x: Interval, y: Interval, fn: Callable[[Number, Number], Number]
) -> Interval:
    """
    ### Description
    Computes any arbitrary binary function, of type `Number -> Number -> Number`, on the
    two input intervals. For small arithmetic expressions the `operator` module could be
    handy. Otherwise, a `lambda` expression is usually preferred.
    """
    x1, x2, y1, y2 = (
        x.lower_bound,
        x.upper_bound,
        y.lower_bound,
        y.upper_bound,
    )
    possible_bounds: list[Number] = [fn(x1, y1), fn(x1, y2), fn(x2, y1), fn(x2, y2)]
    return Interval(
        min(possible_bounds),
        max(possible_bounds),
    )


def rand_uniform(interval: Interval, *, values: int = 1) -> list[float]:
    """
    Return a random float within finite interval.
    """
    if abs(interval.adjusted_lower_bound) == float("inf") or abs(
        interval.upper_bound
    ) == float("inf"):
        raise ValueError(f"bounds of interval (was {interval}) must be finite")

    def f(i: Interval) -> float:
        return random.random() * i.diameter + i.lower_bound

    return [f(interval) for _ in range(values)]


def rand_interval(
    lower_bound_interval: Interval, upper_bound_interval: Interval
) -> Interval:
    return Interval(
        rand_uniform(lower_bound_interval)[0],
        rand_uniform(upper_bound_interval)[0],
    )


def lerp(interval: Interval, t: Number) -> Number:
    return interval.adjusted_lower_bound + t * interval.diameter


def invlerp(interval: Interval, value: Number) -> Number:
    return (value - interval.adjusted_lower_bound) / interval.diameter


def remap(interval1: Interval, interval2: Interval, value: Number) -> Number:
    t: Number = invlerp(interval1, value)
    return lerp(interval2, t)
