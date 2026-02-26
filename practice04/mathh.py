import random

a, b = random.randint(1, 9), random.randint(1, 9)
op = random.choice(["+", "-", "*", "/"])

if op == "+":
    result = a + b
elif op == "-":
    result = a - b
elif op == "*":
    result = a * b
else:
    result = a / b

print(f"{a} {op} {b} = {result}")

