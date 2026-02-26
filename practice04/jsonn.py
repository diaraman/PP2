import json

# A Python dictionary
student = {"name": "Alice", "age": 20, "is_student": True}

# Converting Python dictionary -> JSON string.
# indent=2 makes the output pretty and easy to read(indent=2 means 2 spaces)
json_text = json.dumps(student, indent=2)
print("Python dict -> JSON:")
print(json_text)


