names = ["Ali", "Dana", "Aruzhan"]
scores = [90, 85, 95]

# enumerate(): index + value
print("Enumerate examples:")
for index, name in enumerate(names, start=1):
    print(index, name)

# zip(): to pair
print("\nZip examples:")
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# type checking + conversions
print("\nType checking and conversions:")
x = "123"
print("x:", x, "| type:", type(x))

x_int = int(x)
print("x_int:", x_int, "| type:", type(x_int), "| isinstance(int):", isinstance(x_int, int))

y = 10
y_float = float(y)
print("y_float:", y_float, "| type:", type(y_float))

z = [1, 2, 3]
z_tuple = tuple(z)
print("z_tuple:", z_tuple, "| type:", type(z_tuple))
