# Class with constructor (__init__) for initial values.
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age


# Create an instance with constructor arguments.
s = Student("Ali", 19)
print(s.name, s.age) # Output: Ali 19
