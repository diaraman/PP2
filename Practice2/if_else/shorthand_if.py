a = 5
b = 2
if a > b: print("a is greater than b")

a = 67
b = 16
print("a > b" if a > b else "a <= b")

a = 67
b = 16
print("a > b") if a > b else print("a <= b")

a = 67
b = 1488
bigger = a if a > b else b
print(f"Bigger is: {bigger}")

a = 67
b = 67
print("a > b") if a > b else print("a == b") if a == b else print("a < b")