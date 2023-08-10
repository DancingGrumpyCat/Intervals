# create a half-open Interval object <(0, 5]>
x = Interval(0, 5, include_start=False)

print(x) # Interval(0, 5]

# the step method creates a generator yielding only values within the interval, starting at start and ending at end
# this is similar to range(), but offers an abstraction where you can have more than one range based on the same interval
print(list(x.step(2, start=-1)))
print(list(x.step(2)))

print(x.interval_type) # open, closed, or half-open; returns a string
print(x.magnitude) # difference between end and start; returns a float

print(4 in x) # True
print(0 in x) # False
