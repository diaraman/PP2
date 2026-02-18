# Parent class stores father's name.
class Parent:
    def __init__(self, father_name):
        self.father_name = father_name

    def father_info(self):
        return "My father's name is " + self.father_name


# Child class stores child's own name and age, and gets father_name via super().
class Child(Parent):
    def __init__(self, child_name, father_name):
        super().__init__(father_name)
        self.child_name = child_name

    def profile(self):
        return f"My name is {self.child_name}. {self.father_info()}."



c = Child("Madi", "Askar")
print(c.profile())
