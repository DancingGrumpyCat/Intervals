import pytest
from intervals import Interval


# TODO: generate a few random intervals and test them
x = Interval(0, 5)


def test_init() -> None:
    assert x.upper_bound >= x.lower_bound
    assert x.apparent_upper_bound <= x.upper_bound
    assert x.apparent_lower_bound >= x.lower_bound


def test_infinite() -> None:
    from itertools import islice

    inf = float("inf")

    x = Interval(0, inf)
    y = Interval(-inf, 0)
    z = Interval(-inf, inf)

    assert x.diameter == y.diameter == z.diameter == inf
    assert list(islice(x.step(1), 4)) == [0, 1, 2, 3]
    assert x + 1 == Interval(1, inf)
    assert x * -1 == y


# real world example
def test_binary_fn() -> None:
    weight: Interval = Interval.from_plus_minus(80, 0.5)
    height: Interval = Interval.from_plus_minus(1.79, 0.005)
    bmi: Interval = weight.binary_fn(height, lambda x, y: x / y**2)
    assert str(bmi.truncate(3)) == "[24.673, 25.266]"


def test_to_from_plusminus() -> None:
    assert (
        str(Interval.from_plus_minus(string=x.as_plus_minus(precision=3)))
        == "[0.0, 5.0)"
    )


# step can't be the identity element
def test_step_zero_fail() -> None:
    with pytest.raises(ZeroDivisionError):
        print(list(x.step(0)))
