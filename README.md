# Intervals

Python module supporting math intervals.
Functions as an abstraction and superset of the range function.

Many methods and examples herein are taken from
[Interval Arithmetic&mdash;Wikipedia](https://en.wikipedia.org/wiki/Interval_arithmetic)
.

## Basic usage example

```pycon
>>> # INITIALIZATION
>>> interval_1 = Interval.from_string("[0, 5)")  # [0, 5)
>>> interval_2 = Interval(3, 6)  # [3, 6)

>>> # METHODS & PROPERTIES
>>> print(interval_1)
[0, 5)
>>> list(interval_1.step(2))
[0, 2, 4]
>>> list(interval_1.step(2, start=-1))
[1, 3, 5]
>>> list(interval_1.step(-1, start=5))  # does not include 5 because upper_bound is open
[4, 3, 2, 1, 0]
>>> interval_1.interval_type
'half-open'
>>> interval_1.diameter
5
>>> 4 in interval_1
True
>>> 0 in interval_1
False
>>> print(interval_1 + 2)
[2, 7)
>>> print(-interval_1)  # note that the closed and opened bounds swap order too
(-5, 0]
>>> print(5 // interval_1)
[1, inf)
>>> print(interval_1 & interval_2)
[3, 5]
>>> print(interval_1 | interval_2)
(0, 6)
>>> print((interval_1 + interval_2) / 2)
[1.5, 5.5]
```

## Plus-Minus form

```pycon
>>> interval_3 = Interval.from_string("2 +- 1.2")
>>> print(interval_3)
[0.8, 3.2)
```

The diameter of such an interval will be double its plus/minus value.

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

```pycon
>>> from math import tau
>>> import numpy as np
>>> print(np.array(list(Interval(0, tau).step(tau / 24))) ** 2)
[ 0.          0.06853892  0.27415568  0.61685028  1.09662271  1.71347299
  2.4674011   3.35840705  4.38649084  5.55165248  6.85389195  8.29320925
  9.8696044  11.58307739 13.43362821 15.42125688 17.54596338 19.80774772
 22.2066099  24.74254992 27.41556778 30.22566348 33.17283701 36.25708839]
```

## Arithmetic operations between two intervals

```python
>>> weight = Interval.from_string("80 +- 0.5")  # accurate to the nearest kg
>>> height = Interval.from_string("1.79 +- 0.005")  # accurate to the nearest cm
>>> bmi = weight / height ** 2
>>> print(round(bmi, 3))
[24.673, 25.266)
```

## Infinity

You can create infinite (unbounded) intervals. I recommend combining this with the `itertools` modules `islice` and `takewhile`.

Any side that is unbounded like this must be closed; doing `integers = Interval(-inf, +inf, lower_closure="open")` does the same thing as `integers = Interval(-inf, +inf, lower_closure="closed")`.

### Using `itertools`

```python
>>> from intervals.constants import POSITIVE_REALS
>>> from itertools import islice, takewhile
>>> interval_4 = POSITIVE_REALS + 1
>>> n_1mod4 = interval_4.step(4)
```

```python
>>> list(islice(n_1mod4, 10))
[1, 5, 9, 13, 17, 21, 25, 29, 33, 37]
```

```python
from random import random
>>> list(takewhile(lambda _: random() > 1/4, n_1mod4))
[1, 5, 9, 13, 17]
```

## Utils

```python
interval_5 = Interval(0, 5)
interval_6 = Interval(3, 12)
```

### `rand_uniform`

(Uses `random.random`&mdash;not cryptographically secure.) Generates `values` random floats within the interval's bounds.

```python
>>> utils.rand_uniform(interval_5)
[3.184482794264942]
>>> utils.rand_uniform(interval_5, values=5)
[3.1222991463963361,
 2.2991947013044474,
 2.8317198384298465,
 4.1059785415505439,
 1.7879902265000007]
```

### `lerp`, `invlerp`, and `remap`

```python
>>> utils.lerp(interval_5, 0.3)
1.5
>>> utils.invlerp(interval_5, 1.5)
0.3
>>> utils.remap(interval_5, interval_6, 2.5)
7.5
```
