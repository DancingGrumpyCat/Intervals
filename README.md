# Intervals
Python module supporting math intervals.
Functions as an abstraction and superset of the range function.

Many methods and examples herein are taken from [https://en.wikipedia.org/wiki/Interval_arithmetic].


## Basic usage example
```python
# INITIALIZATION
interval_1 = Interval(Bounds(0, 5, lower_closure="open"))
interval_2 = Interval(Bounds(3, 6, upper_closure="closed"))

# METHODS & PROPERTIES
str(interval_1) # 'Interval(0, 5]'
list(interval_1.step(2, start=-1)) # [1, 3, 5]
list(interval_1.step(2)) # [2, 4]
interval_1.interval_type # 'half-open'
interval_1.diameter # 5
4 in interval_1 # True
0 in interval_1 # False
interval_1 + 2 # (2, 7]
interval_1 * -1 # [-5, 0) # NOTE the closed and opened bounds swapped order too
interval_1 & interval_2 # [3, 5]
interval_1 | interval_2 # (0, 6)
```


## Plus-Minus form
```python
interval_3 = Interval.from_plus_minus(2, 1.2)
str(interval_3) # 'Interval[0.8, 3.2]'
```
The diameter of such an interval will be double its plus/minus value.

The following (all spaces are removed, so others are also possible) are also equivalent:
```python
Interval.from_plus_minus(2, 1.2)
Interval.from_plus_minus("2 +- 1.2")
Interval.from_plus_minus("2 +/- 1.2")
Interval.from_plus_minus("2 ± 1.2")
Interval.from_plus_minus("2 pm 1.2")
Interval.from_plus_minus("2 p/m 1.2")
```


## How it can replace `range`
Instead of
```python
[x**2 for x in range(10, 15, 2)]
```
you can now write
```python
[x**2 for x in Interval(Bounds(10, 14)).step(2)]
```
and you can do a lot more, like floating point values:
```python
tau = 6.283_185_307
[x**2 for x in Interval(Bounds(-tau, tau)).step(tau / 4)]
```

## Arithmetic operations between two intervals
Use the `binary_fn` method.

```python
>>> weight = Interval.from_plus_minus(80, 0.5) # accurate to the nearest kg
>>> height = Interval.from_plus_minus(1.79, 0.005) # accurate to the nearest cm
>>> bmi = weight.binary_fn(height, lambda x, y: x / y**2)
>>> bmi.truncate(3)
[24.673, 25.266]
```


## Infinity

You can create infinite (unbounded) intervals. I recommend combining this with the `itertools` `islice` module.

```python
inf = float("inf")

negative = Interval(-inf, 0)
positive = Interval(0, +inf)
integers = Interval(-inf, +inf)
```

(Any side that is unbounded like this must be closed; doing `integers = Interval(-inf, +inf, includes_lower_bound=False)` does the same thing as `integers = Interval(-inf, +inf, includes_lower_bound=True)`.)

### Using `itertools`

The following examples assume `*` is imported from `itertools`.

```python
>>> interval_4 = Interval(1, float("inf"))
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
(Uses `random.random`&mdash;not cryptographically secure.)
```python
>>> utils.rand_uniform(interval_5)
3.184482794264942
>>> utils.rand_uniform(interval_5, values=5)
[3.1222991463963361,
 2.2991947013044474,
 2.8317198384298465,
 4.1059785415505439,
 1.7879902265000007]
```
### `lerp`, `invlerp`, and `remap`
<aside><b>TODO</b>: add varargs support for <code>t</code> and <code>value</code>.</aside>

```python
>>> utils.lerp(interval_5, 0.3)
1.5
>>> utils.invlerp(interval_5, 1.5)
0.3
>>> utils.remap(interval_5, interval_6, 2.5)
7.5
```
