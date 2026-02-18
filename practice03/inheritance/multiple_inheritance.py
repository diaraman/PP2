# First parent class.
class Flyable:
    def fly(self):
        print("Flying")


# Second parent class.
class Swimmable:
    def swim(self):
        print("Swimming")


# Child inherits behavior from both parents.
class Duck(Flyable, Swimmable):
    pass


d = Duck()
d.fly()
d.swim()
