## 1.py
This one converts degrees to radians using the `math` library.

```python
import math

degree = 15
radian = math.radians(degree)

print("Output radian:", round(radian, 6))
```

## 2.py
Here we calculate the area of a trapezoid from user input.

```python
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))

area = (base1 + base2) / 2 * height
print("Expected Output:", area)
```

## 3.py
This program finds the area of a regular polygon by number of sides and side length.

```python
import math

n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))

area = (n * s * s) / (4 * math.tan(math.pi / n))
print("The area of the polygon is:", area)
```

## 4.py
Simple area of a parallelogram: `base * height`.

```python
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))

area = base * height
print("Expected Output:", area)
```
