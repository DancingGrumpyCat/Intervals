import pytest
from intervals import Interval, clamp, rand_uniform, lerp, invlerp
from intervals import Number, Bounds, EMPTY_SET

x = Interval(0, 5)


def test_clamp() -> None:
    assert clamp(6, x) == 5
    assert clamp(-1, x) == 0
    assert clamp(3, x) == 3


def test_rand_uniform() -> None:
    for _ in Interval(0, 1000, lower_closure="open").step(1):
        assert x.lower_bound <= rand_uniform(x)[0] <= x.upper_bound


# lerp and invlerp are inverses of each other, so applying both needs to do nothing
def test_lerp_invlerp_inverses() -> None:
    t0 = 0.5
    value: Number = lerp(x, t0)
    t1: Number = invlerp(x, value)
    assert t0 == t1


# no value can be clamped to the empty set
def test_clamp_fail() -> None:
    with pytest.raises(ValueError):
        x1: Interval = EMPTY_SET
        clamp(3, x1)


# no value can be within the empty set, so a value's percentage from the lower to upper
# bound is undefined
def test_invlerp_fail() -> None:
    with pytest.raises(ZeroDivisionError):
        x1: Interval = EMPTY_SET
        invlerp(x1, 5)
