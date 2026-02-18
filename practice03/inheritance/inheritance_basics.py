# Parent class.
class Animal:
    def speak(self):
        print("Animal sound")


# Child class inherits from Animal.
class Dog(Animal):
    pass

# Inherited method is available in child object.
d = Dog()
d.speak()
