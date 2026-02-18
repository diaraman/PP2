class Person():
    def __init__(self,name,age):
        self.name = name
        self.age = age

    def intro(self):
        print(self.name,self.age)

p1 = Person("John",34)
p1.intro()



class Company():
    def __init__(self,name):
        self.name = name

    def change_name(self,new_name):
        self.name = new_name

c1 = Company("Bosh")
print(c1.name)
c1.change_name("Smeg")
print(c1.name)