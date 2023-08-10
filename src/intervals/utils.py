import random

from intervals.intervals import Interval, Number


def clamp(value: Number, interval: Interval) -> Number:
    return min(interval.actual_end, max(interval.actual_start, value))


def rand_uniform(interval: Interval, *, values: int = 1) -> float | list[float]:
    def f(i: Interval) -> float:
        return random() * i.magnitude + i.actual_start

    if values == 1:
        return f(interval)
    return [f(interval) for _ in range(values)]
