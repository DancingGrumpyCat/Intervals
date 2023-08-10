from intervals import Interval, clamp, rand_uniform

x = Interval(0, 5)


def test_clamp() -> None:
    assert clamp(6, x) == 5
    assert clamp(-1, x) == 0


def test_rand_uniform() -> None:
    assert x.actual_start <= rand_uniform(x) <= x.actual_end
