# Using super() to call parent constructor
class Parent:
    def __init__(self):
        print("Parent initialized")

class Child(Parent):
    def __init__(self):
        super().__init__()
        print("Child initialized")

c = Child()

# Passing one argument to parent
class Device:
    def __init__(self, name):
        self.name = name

class Phone(Device):
    def __init__(self, name):
        super().__init__(name)

p = Phone("iPhone")
print(p.name)

# Initializing multiple attributes
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

class Admin(User):
    def __init__(self, username, email, level):
        super().__init__(username, email)
        self.level = level

adm = Admin("root", "test@test.com", 1)
print(adm.username, adm.level)

# Calling parent method inside child method
class Base:
    def greet(self):
        return "Hello"

class Custom(Base):
    def greet(self):
        msg = super().greet()
        return f"{msg} from Child"

obj = Custom()
print(obj.greet())
