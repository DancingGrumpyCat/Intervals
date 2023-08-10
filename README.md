# Intervals
Python module supporting math intervals as an abstraction and superset of the range function.

## Basic usage examples
```python
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

## How it replaces `range`
Instead of
```python
>>> [x**2 for x in range(10, 15, 2)]
```
you can now write
```python
>>>[x**2 for x in Interval(10, 14).step(2)]
```
