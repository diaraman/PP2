# Parent class with shared behavior.
class Bird:
    def move(self):
        print("Bird is moving")

    def lay_eggs(self):
        print("Bird lays eggs")


# Inherited version: move() is overridden, other Bird methods stay available.
class Penguin(Bird):
    def move(self):
        print("Penguin is swimming")


# Non-inherited version: same move() output, but no Bird features.
class PenguinNoInherit:
    def move(self):
        print("Penguin is swimming")


p1 = Penguin()
p2 = PenguinNoInherit()

print("Same move() output:")
p1.move()
p2.move()

print("Difference:")
p1.lay_eggs()  # Works because Penguin inherits Bird.

