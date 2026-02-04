x = 7
y = 3
print(x > 5 and y < 11) # True and True --> True
print(x > 5 and y > 5) # True and False --> False

x = 12
y = 18
print(x > 10 or y > 10) # True or True --> True
print(x < 10 or y > 10) # False or True --> True
print(x > 30 or y < 0) # False or False --> False

x = 14
y = 88
print(not(x == y)) # not False => True
print(not(x > y and y < 67)) # not (False and False) => not False => True