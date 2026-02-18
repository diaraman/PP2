# Basic parent class
class Animal:
    def eat(self):
        print("Eating...")

# Child inherits from Animal
class Dog(Animal):
    def bark(self):
        print("Barking...")

d = Dog()
d.eat()
d.bark()

# Inheriting basic attributes
class Vehicle:
    brand = "Toyota"

class Car(Vehicle):
    model = "Camry"

my_car = Car()
print(my_car.brand, my_car.model)

# Person and Employee relationship
class Person:
    def info(self):
        print("This is a person")

class Employee(Person):
    salary = 5000

staff = Employee()
staff.info()
print(staff.salary)

# Shape and Rectangle logic
class Shape:
    color = "Red"

class Rectangle(Shape):
    def area(self, w, h):
        return w * h

rect = Rectangle()
print(rect.color, rect.area(10, 5))
