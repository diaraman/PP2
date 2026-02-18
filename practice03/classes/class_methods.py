# Class 
class MathTools:
    def __init__(self, a, b): # Constructor to initialize attributes
        self.a = a 
        self.b = b 

    def multiply(self):# Method to multiply a and b
        return self.a * self.b



p=MathTools(3, 4)# Create an object of MathTools with a=3 and b=4

print(p.multiply()) # Call the multiply method and print the result