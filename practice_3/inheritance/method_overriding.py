# Overriding a simple method
class Bird:
    def fly(self):
        print("Flying high")

class Penguin(Bird):
    def fly(self):
        print("Cannot fly")

p = Penguin()
p.fly()

# Changing output of a display method
class Test:
    def show(self):
        print("Default test")

class Final(Test):
    def show(self):
        print("Final result")

f = Final()
f.show()

# Payment logic override
class Payment:
    def process(self):
        print("Generic payment")

class PayPal(Payment):
    def process(self):
        print("Processing via PayPal API")

pay = PayPal()
pay.process()

# Discount calculation override
class StandardPrice:
    def calculate(self, price):
        return price

class DiscountPrice(StandardPrice):
    def calculate(self, price):
        return price * 0.8

price_tool = DiscountPrice()
print(price_tool.calculate(100))
