import pytest
from intervals import Interval


def test_init() -> None:
    x = Interval(0, 5)  # TODO: generate a few random intervals and test them
    assert x.upper_bound >= x.lower_bound
    assert x.apparent_upper_bound <= x.upper_bound
    assert x.lower_bound <= x.upper_bound


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


# step can't be the identity element
def test_step_zero_fail() -> None:
    with pytest.raises(ZeroDivisionError):
        x = Interval(0, 5)
        print(list(x.step(0)))
