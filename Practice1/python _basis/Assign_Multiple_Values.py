#there we can see 3 examples how can Assign Multiple Values
# Number1 - Many Values to Multiple Variables
x,y,z="Orange","Banana","Cherry"
print(x)
print(y)
print(z)

# Nunber2 - One Value to Multiple Variables
x = y = z = "Orange"
print(x)
print(y)
print(z)

# Number3 - Unpack a Collection (list,tuple,set, etc.)
fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)
