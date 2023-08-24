# TODO

## Features

- [ ] Change `epsilon` out for something like `math.nextfloat`
- [ ] Fuzzy sets:
  - [ ] Figure out logic & arithmetic between fuzzy sets
    - Source:
      - L.A. Zadeh,
      - Fuzzy sets, Information and Control, Volume 8, Issue 3, 1965, Pages 338-353.
      - ISSN 0019-9958.
      - [Digital Object Identifier Foundation](https://doi.org/10.1016/S0019-9958(65)90241-X).
  - [ ] Extra methods:
    - Integration? Maybe the user can do that using `sympy`.
    - Intersection (`&`) and union (`|`) need to be changed.
- [ ] Add varargs option for lerp, invlerp, and remap
- [ ] Add Region parent class
  - [ ] Multidimensional version of intervals.
- [ ] Add CircularArc child class
  - [ ] Adds method `arc_length(self, radius: Number) -> Number` equal to width * radius
  - [ ] Adds method `to_bounding_box(self) -> tuple[Interval, Interval]` returning the smallest orthogonal region on the plane as a pair of intervals
- [ ] Support complex-valued Intervals

## Bugs
