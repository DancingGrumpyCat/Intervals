import pytest
from intervals import (
    Interval,
    ADDITIVE_IDENTITY,
    EMPTY_SET,
    UNIT,
    NEGATIVE_UNIT,
    UNIT_DISK,
)


# TODO: generate a few random intervals and test them
x = Interval(0, 5)


# bounds must be in the right order
def test_init() -> None:
    assert x.upper_bound >= x.lower_bound
    assert x.upper_bound <= x.adjusted_upper_bound
    assert x.lower_bound >= x.adjusted_lower_bound


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

    # test default infinity
    assert Interval(float("-inf"), float("inf")) == Interval.from_string("[,]")
    assert Interval(0, float("inf")) == Interval.from_string("[0,]")
    assert Interval(float("-inf"), 0) == Interval.from_string("[,0]")

    # test constants
    assert ADDITIVE_IDENTITY == Interval.from_string("[0, 0]")
    assert EMPTY_SET == Interval.from_string("(0, 0)")
    assert UNIT == Interval.from_string("(0, 1]")
    assert UNIT_DISK == Interval.from_string("[-1, 1]")


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
    x = Interval(0.21405899944813878, 9.463497115948577)
    assert str(x.truncate(+100)) == "[0.21405899944813878, 9.463497115948577)"
    assert str(x.truncate(+10)) == "[0.2140589994, 9.463497116)"
    assert str(x.truncate(+5)) == "[0.21405, 9.4635)"
    assert str(x.truncate(+1)) == "[0.2, 9.5)"
    assert str(x.truncate(-1)) == "[-0.0, 10.0)"
    assert str(x.truncate(-2)) == "[-0.0, 100.0)"


def test_step() -> None:
    assert list(NEGATIVE_UNIT.step(1 / 4)) == [-1.0, -0.75, -0.5, -0.25, 0.0]
    assert list(UNIT.step(1 / 4)) == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert list(UNIT_DISK.step(1 / 2)) == [-1.0, -0.5, 0.0, 0.5, 1.0]
    assert list(x.step(-1, start=5)) == [5, 4, 3, 2, 1, 0]
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
    assert x * -1 == ~(-x) == Interval(-5, 0)
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

    x = Interval(0, inf)
    y = Interval(-inf, 0)
    z = Interval(-inf, inf)

    assert x.diameter == y.diameter == z.diameter == inf
    assert list(islice(x.step(1), 4)) == [0, 1, 2, 3]
    assert x + 1 == Interval(1, inf)
    assert x * -1 == y


# real world example
def test_binary_fn() -> None:
    height: Interval = Interval.from_string("1.79 +- 0.005")  # meters
    weight: Interval = Interval.from_string("80 +- 0.5")  # kilograms
    bmi: Interval = weight / height**2
    assert str(bmi.truncate(3)) == "[24.673, 25.266)"


# from_string undoes as_plus_minus (but not necessarily the other way around)
def test_as_plus_minus() -> None:
    assert (
        str(Interval.from_string(interval_string=x.as_plus_minus(precision=3)))
        == "[0.0, 5.0)"
    )


# step can't be the identity element
def test_step_zero_fail() -> None:
    with pytest.raises(ValueError):
        print(list(x.step(0)))
