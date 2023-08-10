import pytest
from intervals import Interval


def test_init() -> None:
    x = Interval(0, 5)
    assert x.apparent_start >= x.actual_start
    assert x.apparent_end <= x.actual_end
    assert x.actual_start <= x.actual_end


def test_init_fail() -> None:
    with pytest.raises(ValueError):
        _ = Interval(5, 0)
