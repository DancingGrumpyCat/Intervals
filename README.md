# Intervals
Python module supporting math intervals as an abstraction and superset of the range function.

## Basic usage examples
```python3
>>> x = Interval(0, 5, include_start=False)
>>> str(x)
'Interval(0, 5]'
>>> list(x.step(2, start=-1))
[1, 3, 5]
>>> list(x.step(2))
[2, 4]
>>> x.interval_type
'half-open'
>>> x.magnitude
5
>>> 4 in x
True
>>> 0 in x
False
```
