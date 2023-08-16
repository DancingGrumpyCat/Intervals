import pytest
from intervals import (
    Interval,
    EMPTY_SET,
    UNIT,
    POSITIVE_REALS,
    UNIT_DISK,
    _INF,
)


# TODO: generate a few random intervals and test them
x = Interval(0, 5)


# bounds must be in the right order
def test_init() -> None:
    assert x.upper_bound >= x.lower_bound
    assert x.upper_bound >= x.adjusted_upper_bound
    assert x.lower_bound <= x.adjusted_lower_bound
    assert (-x).upper_bound >= (-x).adjusted_upper_bound


def test_str() -> None:
    # test bound types
    assert Interval(
        0, 5, lower_closure="closed", upper_closure="closed"
    ) == Interval.from_string("[0, 5]")
    assert Interval(
        0, 5, lower_closure="open", upper_closure="closed"
    ) == Interval.from_string("(0, 5]")
    assert Interval(
        0, 5, lower_closure="closed", upper_closure="open"
    ) == Interval.from_string("[0, 5)")
    assert Interval(
        0, 5, lower_closure="open", upper_closure="open"
    ) == Interval.from_string("(0, 5)")

    inf = float("inf")
    # test default infinity
    assert Interval(-inf, inf).closed() == Interval.from_string("[,]")
    assert Interval(0, inf).closed() == Interval.from_string("[0,]")
    assert -Interval(0, inf).closed() == Interval.from_string("[,0]")

    # test constants
    assert EMPTY_SET == Interval.from_string("(0, 0)")
    assert UNIT == Interval.from_string("[0, 1)")
    assert UNIT_DISK == Interval.from_string("[-1, 1]")
    assert POSITIVE_REALS == Interval.from_string("[0, ]")


def test_repr() -> None:
    w = Interval(0, 5, lower_closure="closed", upper_closure="closed")
    assert (
        repr(w) == "Interval("
        "lower_bound=0, upper_bound=5, "
        "lower_closure=closed, upper_closure=closed)"
    )
    x = Interval(0, 5, lower_closure="open", upper_closure="closed")
    assert (
        repr(x) == "Interval("
        "lower_bound=0, upper_bound=5, "
        "lower_closure=open, upper_closure=closed)"
    )
    y = Interval(0, 5, lower_closure="closed", upper_closure="open")
    assert (
        repr(y) == "Interval("
        "lower_bound=0, upper_bound=5, "
        "lower_closure=closed, upper_closure=open)"
    )
    z = Interval(0, 5, lower_closure="open", upper_closure="open")
    assert (
        repr(z) == "Interval("
        "lower_bound=0, upper_bound=5, "
        "lower_closure=open, upper_closure=open)"
    )
    assert (
        repr(EMPTY_SET) == "Interval("
        "lower_bound=0, upper_bound=0, "
        "lower_closure=open, upper_closure=open)"
    )


def test_contains() -> None:
    assert x.lower_bound - 1 not in x
    assert x.midpoint in x
    assert x.upper_bound + 1 not in x

    assert x.adjusted_lower_bound in x
    assert x.adjusted_upper_bound in x

    # exactly one of these is true
    assert (x.lower_bound not in x) + (x.lower_closure == "closed") == 1
    # exactly one of these is true
    assert (x.upper_bound not in x) + (x.upper_closure == "closed") == 1


def test_truncate() -> None:
    x = Interval(0.21405899944813878, 8.463497115948577)
    assert round(x, +100) == Interval.from_string(
        "[0.21405899944813878, 8.463497115948577)"
    )
    assert round(x, +10) == Interval.from_string("[0.2140589994, 8.463497116)")
    assert round(x, +5) == Interval.from_string("[0.21405, 8.4635)")
    assert round(x, +1) == Interval.from_string("[0.2, 8.5)")
    assert round(
        x,
    ) == Interval.from_string("[0, 9)")
    assert round(x, 0) == Interval.from_string("[0, 9)")
    assert round(x, -1) == Interval.from_string("[0, 10)")
    assert round(x, -2) == Interval.from_string("[0, 100)")


def test_step() -> None:
    assert list((-UNIT).step(1 / 4)) == [-0.75, -0.5, -0.25, 0.0]
    assert list(UNIT.step(1 / 4)) == [0, 0.25, 0.5, 0.75]
    assert list(UNIT_DISK.step(1 / 2)) == [-1.0, -0.5, 0.0, 0.5, 1.0]
    assert list(x.step(-1, start=5)) == [4, 3, 2, 1, 0]
    assert list(x.step(2)) == [0, 2, 4]


def test_steps() -> None:
    assert list(f"{x:.6f}" for x in UNIT.steps(7)) == [
        "0.000000",
        "0.142857",
        "0.285714",
        "0.428571",
        "0.571429",
        "0.714286",
        "0.857143",
        "1.000000",
    ]


def test_math() -> None:
    assert x + 2 == Interval(2, 7)
    assert x - 2 == Interval(-2, 3)
    assert x * 2 == Interval(0, 10)
    assert x * -1 == -x == ~Interval(-5, 0)
    assert x / 2 == Interval(0.0, 2.5)
    assert x // 2 == Interval(0, 2)

    y = Interval(0, 5, lower_closure="open")  # (0, 5]
    z = Interval(3, 6, upper_closure="open")  # [3, 6)
    assert y.intersects(z)
    assert y & z == Interval(3, 5)  # [3, 5]
    assert y | z == Interval(0, 6, lower_closure="open", upper_closure="open")  # (0, 6)


def test_infinite() -> None:
    from itertools import islice

    inf = float("inf")

    x = Interval(0, _INF)
    y = Interval(-_INF, 0)
    z = Interval(-_INF, _INF)

    assert x.width == y.width == z.width == _INF

    assert list(islice(x.step(1), 4)) == [0, 1, 2, 3]

    assert x + 1 == Interval(1, _INF)
    assert ~x * -1 == y


def test_helper_round() -> None:
    assert Interval._round(-3.0, 0, -1) == -3
    assert Interval._round(-3.5, 0, -1) == -4
    assert Interval._round(-3.5, 0, +1) == -3
    assert Interval._round(+3.0, 0, +1) == +3
    assert Interval._round(+3.5, 0, +1) == +4
    assert Interval._round(+3.5, 0, -1) == +3


# real world example
def test_binary_fn() -> None:
    height: Interval = Interval.from_string("1.79 +- 0.005")  # meters
    weight: Interval = Interval.from_string("80 +- 0.5")  # kilograms
    bmi: Interval = weight / height**2
    assert str(round(bmi, 3)) == "[24.673, 25.266)"


# from_string undoes as_plus_minus (but not necessarily the other way around)
def test_as_plus_minus() -> None:
    assert str(Interval.from_string(x.as_plus_minus(precision=3))) == "[0.0, 5.0)"


# step can't be the identity element
def test_step_zero_fail() -> None:
    with pytest.raises(ValueError):
        print(list(x.step(0)))
