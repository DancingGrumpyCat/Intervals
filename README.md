# Intervals
Python module supporting math intervals as an abstraction and superset of the range function.

## Basic usage examples
```python3
>>> x = Interval(0, 5, include-start=False)
>>> print(x)
Interval(0, 5]
>>> print(list(x.step(2, start=-1)))
[1, 3, 5]
>>> print(list(x.step(2))
[2, 4]
>>> print(x.interval_type)
half-open
>>> print(x.magnitude)
5
```
