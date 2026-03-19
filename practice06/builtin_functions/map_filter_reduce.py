from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map(): to affect all numbers to show their square
squares = list(map(lambda x: x * x, numbers))

# filter(): to filter only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))

# reduce(): to reduce a list into a one number
total = reduce(lambda a, b: a + b, numbers)

print("Numbers:", numbers)
print("Squares (map):", squares)
print("Evens (filter):", evens)
print("Total (reduce):", total)
