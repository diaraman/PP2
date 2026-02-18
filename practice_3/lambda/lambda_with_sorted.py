numbers = [5, 2, 8, 1]
sorted_numbers = sorted(numbers, key=lambda x: x)
print(sorted_numbers)



students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)



words = ["apple", "kiwi", "banana"]
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)