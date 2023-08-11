import pytest
from intervals import Interval, clamp, rand_uniform, lerp, invlerp
from intervals import Number

x = Interval(0, 5)


def test_clamp() -> None:
    assert clamp(6, x) == 5
    assert clamp(-1, x) == 0


def test_rand_uniform() -> None:
    for _ in Interval(0, 1000).step(1):
        assert x.actual_start <= rand_uniform(x) <= x.actual_end


def test_lerp_invlerp_inverses() -> None:
    t0 = 0.5
    value: Number = lerp(x, t0)
    t1: Number = invlerp(x, value)
    assert t0 == t1


def test_clamp_fail() -> None:
    with pytest.raises(ValueError):
        x1 = Interval(0, 0, include_start=False, include_end=False)
        clamp(3, x1)


def test_invlerp_fail() -> None:
    with pytest.raises(ZeroDivisionError):
        x1 = Interval(0, 0, include_start=False, include_end=False)
        invlerp(x1, 5)
