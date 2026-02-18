# Source list.
numbers = [1, 2, 3, 4, 5, 6]

# Keep only even numbers.
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print(even_numbers)
