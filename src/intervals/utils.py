import random

from intervals.intervals import Interval, Number


def clamp(value: Number, interval: Interval) -> Number:
    """
    Clamp value to within interval.
    """
    if interval.magnitude == 0:
        raise ValueError("Magnitude of interval must be nonzero.")
    if interval.magnitude < 0:
        raise ValueError(
            "I have no idea how you got this error. \
            Magnitude should always be non-negative."
        )
    return min(interval.actual_end, max(interval.actual_start, value))


def rand_uniform(interval: Interval, *, values: int = 1) -> float | list[float]:
    """
    Return a random float within interval.
    """

    def f(i: Interval) -> float:
        return random.random() * i.magnitude + i.actual_start

    if values == 1:
        return f(interval)
    return [f(interval) for _ in range(values)]
