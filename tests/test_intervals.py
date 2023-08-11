import pytest
from intervals import Interval


def test_init() -> None:
    x = Interval(0, 5)
    assert x.apparent_start >= x.actual_start
    assert x.apparent_end <= x.actual_end
    assert x.actual_start <= x.actual_end


def test_infinite() -> None:
    x = Interval(0, float("inf"))
    y = Interval(float("-inf"), 0)
    z = Interval(float("-inf"), float("inf"))
    assert x.magnitude == float("inf")
    assert y.magnitude == float("inf")
    assert z.magnitude == float("inf")


# lower bound can't be greater than upper bound
def test_init_fail() -> None:
    with pytest.raises(ValueError):
        _ = Interval(5, 0)


# step can't be the identity element
def test_step_zero_fail() -> None:
    with pytest.raises(ValueError):
        x = Interval(0, 5)
        print(list(x.step(0)))
