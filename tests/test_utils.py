from intervals import Interval, clamp


def test_clamp() -> None:
    x = Interval(0, 5)
    assert clamp(6, x) == 5
    assert clamp(-1, x) == 0
