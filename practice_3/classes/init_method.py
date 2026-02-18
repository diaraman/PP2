class Person:
    def __init__(self, name):
        self.name = name

p = Person("Alice")
print(p.name)



class Car:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year

c = Car("Toyota", 2022)
print(c.brand, c.year)



class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

s = Student("Bob", "A")
print(s.name, s.grade)