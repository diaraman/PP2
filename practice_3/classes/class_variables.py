class Person:
    species = "Human"

p1 = Person()
print(p1.species)



class Car:
    wheels = 4

c1 = Car()
c2 = Car()
print(c1.wheels, c2.wheels)


class Student:
    school = "ABC School"

s1 = Student()
Student.school = "XYZ School"
print(s1.school)