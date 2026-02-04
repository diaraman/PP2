age=int(input("Enter your age: "))
has_id=input("Do you have an ID? (yes/no): ").lower()=='yes'
parent_ok=input("Do you have parental permission? (yes/no): ").lower()=='yes'
result = ((age >= 18) and has_id) or parent_ok #it checks whether the person is an adult with ID or has parental permission
print(result) 