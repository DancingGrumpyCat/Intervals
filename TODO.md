# TODO

## Features

- [ ] Add methods to shrink and expand (left, right, centered) intervals
- [ ] Change `epsilon` out for something like `math.nextfloat`
- [ ] Replace `from_plus_minus` to general `from_string` method
  - [ ] Allows for `Interval.from_string("[0, 1)")` or
  - [ ] `Interval.from_string("2 pm 1")` etc.
- [ ] Fuzzy sets:
  - [ ] Figure out logic & arithmetic between such fuzzy sets
    - Source:
      - L.A. Zadeh,
      - Fuzzy sets, Information and Control, Volume 8, Issue 3, 1965, Pages 338-353.
      - ISSN 0019-9958.
      - [Digital Object Identifier Foundation](https://doi.org/10.1016/S0019-9958(65)90241-X).
  - [ ] Extra methods:
    - Integration? Maybe the user can do that using `sympy`.
    - Intersection (`&`) and union (`|`) need to be changed.
- [ ] Comparisons like $>$, $<$, etc. should be implemented both between two `Interval`s and between `Interval` and `Number`.
  - [ ] They should return a value from the interval $\left[0, 1\right]$ (0 representing `False` and 1 representing `True`) where the value is equal to the probability that a point in set A and a point in set B chosen independently, uniformly, at random will agree with the comparison. For this we can treat a real number $x$ as the degenerate interval $\left[x, x\right)$.
    - Given two intervals $A$ and $B$, with real valued bounds $a_1$, $a_2$, $b_1$, and $b_2$, choose two uniform random points $a$ and $b$ from $A$ and $B$ independently.
    - $P(A < B) = \lnot P(b \leq a_2 \land a \geq b_1)$
- [ ] Add varargs option for lerp, invlerp, and remap

## Bugs

- [ ] Setting $x := \left[0, 5\right)$ and doing `list(x.step(-1, start=5))` should return `[4, 3, 2, 1, 0]`, but instead returns `[0]` because $5 \notin x$.
