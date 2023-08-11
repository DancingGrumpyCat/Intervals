import random

from intervals.intervals import Interval, Number


def clamp(value: Number, interval: Interval) -> Number:
    """
    Clamp value to within interval.
    """
    if interval.diameter == 0:
        raise ValueError("Magnitude of interval must be non-zero.")
    if interval.diameter < 0:
        raise ValueError(
            "I have no idea how you got this error. \
            Magnitude should always be non-negative."
        )
    return min(interval.upper_bound, max(interval.lower_bound, value))


def rand_uniform(interval: Interval, *, values: int = 1) -> float | list[float]:
    """
    Return a random float within finite interval.
    """
    if abs(interval.lower_bound) == float("inf") or abs(
        interval.apparent_upper_bound
    ) == float("inf"):
        raise ValueError(f"bounds of interval (was {interval}) must be finite")

    def f(i: Interval) -> float:
        return random.random() * i.diameter + i.lower_bound

    if values == 1:
        return f(interval)
    return [f(interval) for _ in range(values)]


def lerp(interval: Interval, t: Number) -> Number:
    return interval.lower_bound + t * interval.diameter


def invlerp(interval: Interval, value: Number) -> Number:
    return (value - interval.lower_bound) / interval.diameter


def remap(interval1: Interval, interval2: Interval, value: Number) -> Number:
    t: Number = invlerp(interval1, value)
    return lerp(interval2, t)
