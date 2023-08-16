import random

from intervals.intervals import Interval, Number


def rand_uniform(interval: Interval, *, values: int = 1) -> list[float]:
    """
    Return a random float within finite interval.
    """
    if abs(interval.adjusted_lower_bound) == float("inf") or abs(
        interval.upper_bound
    ) == float("inf"):
        raise ValueError(f"bounds of interval (was {interval}) must be finite")

    def f(i: Interval) -> float:
        return random.random() * i.width + i.lower_bound

    return [f(interval) for _ in range(values)]


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
        if interval.lower_closure == interval.upper_closure == "open":
            raise ValueError("cannot clamp any value to empty set")
        return interval.lower_bound
    return min(interval.upper_bound, max(interval.lower_bound, value))


def antipode(value: Number, interval: Interval) -> Number:
    """
    Return the value reflected across the midpoint of the interval
    """
    return interval.midpoint - value


def mod(value: Number, interval: Interval) -> Number:
    """
    Return the value modulus the interval range
    """
    return value % interval.width + interval.lower_bound
