# Child inheriting from two parents
class Father:
    f_name = "John"

class Mother:
    m_name = "Anna"

class Child(Father, Mother):
    pass

c = Child()
print(c.f_name, c.m_name)

# Combining two functionalities
class Logger:
    def log(self):
        print("Logging data...")

class Printer:
    def print_doc(self):
        print("Printing...")

class Machine(Logger, Printer):
    pass

m = Machine()
m.log()
m.print_doc()

# Combining attributes of Engine and Body
class Engine:
    hp = 500

class Body:
    color = "Black"

class SportCar(Engine, Body):
    model = "V12"

sc = SportCar()
print(sc.hp, sc.color, sc.model)

# Animal capabilities combination
class Flyer:
    def move(self):
        print("Flying")

class Swimmer:
    def swim(self):
        print("Swimming")

class Duck(Flyer, Swimmer):
    def info(self):
        print("Duck can do both")

d = Duck()
d.move()
d.swim()
