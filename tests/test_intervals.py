import pytest
from intervals import Interval


def test_init() -> None:
    x = Interval(0, 5)
    assert x._start >= x.start
    assert x._end <= x.end
    assert x.start <= x.end


def test_init_fail() -> None:
    with pytest.raises(ValueError):
        _ = Interval(5, 0)
