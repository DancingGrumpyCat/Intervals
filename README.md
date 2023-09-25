# Intervals

Python module supporting math intervals.
Functions as an abstraction and superset of the range function.

Many methods and examples herein are taken from
[Interval Arithmetic&mdash;Wikipedia](https://en.wikipedia.org/wiki/Interval_arithmetic)
.

## Basic usage example

```ipython
In [1]: # INITIALIZATION

In [2]: interval_1 = Interval.from_string("[0, 5)")  # [0.0, 5.0)

In [3]: interval_2 = Interval(3, 6)  # [3, 6)

In [4]: # METHODS & PROPERTIES

In [5]: print(interval_1)
Out[5]: [0.0, 5.0)

In [6]: list(interval_1.step(2, start=0))
Out[6]: [0, 2, 4]

In [7]: list(interval_1.step(2, start=-1))
Out[7]: [1, 3]

In [8]: list(interval_1.step(-1, start=5))  # does not include 5 because upper_bound is open
Out[8]: [4, 3, 2, 1, 0]

In [9]: interval_1.interval_type
Out[9]: <IntervalType.HALF_OPEN: 'half-open'>

In [10]: interval_1.width
Out[10]: 5.0

In [11]: 0 in interval_1
Out[11]: True

In [12]: 5 in interval_1
Out[12]: False

In [13]: print(interval_1 + 2)
[2.0, 7.0)

In [14]: print(-interval_1)  # note that the closed and opened bounds swap order too
(-5.0, 0.0]

In [15]: print(5 / interval_1)
[1.0, inf)

In [16]: print(interval_1 & interval_2)
[3, 5.0)

>>> print(interval_1 | interval_2)
[0.0, 6)
>>> print((interval_1 + interval_2) / 2)
[1.5, 5.5)
```

## Plus-Minus form

```ipython
In [1]: interval_3 = Interval.from_string("2 +- 1.2")  # 2 plus or minus 1.2

In [2]: print(interval_3)
[0.8, 3.2)

In [3]: print(interval_3.width)
2.4000000000000004
```

The following (all spaces are removed, so others are also possible) are also equivalent:

```python
Interval.from_string("2 pm 1.2")
Interval.from_string("2 +- 1.2")
Interval.from_string("2 +/- 1.2")
Interval.from_string("2 ± 1.2")
Interval.from_string("2 pm 1.2")
Interval.from_string("2 p/m 1.2")
Interval(0.8, 3.2)
```

## How it can replace `range`

Instead of the following examples:

```python
# 1.
for x in range(10):
  ...

# 2.
[x**2 for x in range(10, 15, 2)]
```

you can now write

```python
# 1.
for x in Interval(10):
  ...

# 2.
[x**2 for x in Interval(10, 15).step(2)]
```

and you can do a lot more, like floating point values:

```ipython
In [1]: from math import tau
In [2]: theta = tau / 12
In [3]: print(*(
   ...: Interval(0, tau)
   ...: .closed()
   ...: .step(theta)
   ...: ), sep=",\n")
0,
0.5235987755982988,
1.0471975511965976,
1.5707963267948966,
2.0943951023931953,
2.617993877991494,
3.141592653589793,
3.665191429188092,
4.1887902047863905,
4.71238898038469,
5.235987755982988,
5.759586531581287,
6.283185307179586
```

## Arithmetic operations between two intervals

```ipython
In [1]: weight = Interval.from_string("80 +- 0.5")  # accurate to the nearest kg
In [2]: height = Interval.from_string("1.79 +- 0.005")  # accurate to the nearest cm
In [3]: bmi = weight / height ** 2
In [4]: print(round(bmi, 3))
[24.673, 25.266)
```

## Infinity

You can create infinite (unbounded) intervals. I recommend combining this with the `itertools` modules `islice` and `takewhile`, since the outputs tend to be infinite generators.

Any side that is unbounded like this must be closed; doing `integers = Interval(-inf, +inf, lower_closure="open")` does the same thing as `integers = Interval(-inf, +inf, lower_closure="closed")`.

### Using `itertools`

```ipython
In [1]: from itertools import islice, takewhile

In [2]: from random import random

In [3]: interval_4 = POSITIVE_REALS + 1

In [4]: n_1mod4 = interval_4.step(4)

In [5]: list(islice(n_1mod4, 10))
Out[5]: [1, 5, 9, 13, 17, 21, 25, 29, 33, 37]

In [6]: list(takewhile(lambda _: random() > 1/4, n_1mod4))
Out[6]: [1, 5, 9, 13]


In [7]: list(takewhile(lambda _: random() > 1/4, n_1mod4))
Out[7]: []

In [8]: list(takewhile(lambda _: random() > 1/4, n_1mod4))
Out[8]: [21, 25]
```

## Utils

```ipython
In [1]: interval_5 = Interval(0, 5)
In [2]: interval_6 = Interval(3, 12)
```

### `rand_uniform`

(Uses `random.random`&mdash;not cryptographically secure.) Generates `values` random floats within the interval's bounds.

```ipython
In [3]: rand_uniform(interval_5)
Out[3]: [4.64997216360891]

In [4]: rand_uniform(interval_5, values=5)
Out[4]:
[2.545513603508707,
 0.5394888009944876,
 3.872705211980179,
 0.8273514007287991,
 4.209282455847249]
```

### `lerp`, `invlerp`, and `remap`

```ipython
In [5]: lerp(interval_5, 0.3)
Out[5]: 1.5

In [6]: invlerp(interval_5, 1.5)
Out[6]: 0.3

In [7]: remap(interval_5, interval_6, 2.5)
Out[7]: 7.5
```
