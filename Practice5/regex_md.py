Ex:1
#Write a Python program that matches a string that has an 'a' followed by zero or more 'b''s.
import re
def task1(s):
    return bool(re.fullmatch(r'ab*', s))

print(task1("a"))    # True
print(task1("abb"))   # True


Ex:2
#Write a Python program that matches a string that has an 'a' followed by two to three 'b'.
import re
def task2(s):
    return bool(re.fullmatch(r'ab{2,3}', s))

print(task2("abb"))   # True
print(task2("abbb"))  # True
print(task2("ab"))    # False


Ex:3
#Write a Python program to find sequences of lowercase letters joined with a underscore.
import re
def task3(s):
    return re.findall(r'[a-z]+_[a-z]+', s)

print(task3("hello_world test_example python_regex"))
# ['hello_world', 'test_example', 'python_regex']

Ex:4
#Write a Python program to find the sequences of one upper case letter followed by lower case letters.
import re
def task4(s):
    return re.findall(r'[A-Z][a-z]+', s)

print(task4("Hello World Python REGEX Test"))
#  ['Hello', 'World', 'Python', 'Test']

Ex:5
#Write a Python program that matches a string that has an 'a' followed by anything, ending in 'b'.
import re
def task5(s):
    return bool(re.match(r'^a.*b$', s))

print(task5("a123b"))  # True
print(task5("ab"))     # True
print(task5("a"))      # False


Ex:6
#Write a Python program to replace all occurrences of space, comma, or dot with a colon.
import re
def task6(s):
    return re.sub(r'[ ,.]', ':', s)

print(task6("Hello, world. How are you today?"))
#  Hello:world:How:are:you:today?

Ex:7
#Write a python program to convert snake case string to camel case string.
import re
def task7(s):
    words = s.split('_')
    return words[0] + ''.join(w.capitalize() for w in words[1:])

print(task7("hello_world_example"))
#  helloWorldExample

Ex:8
#Write a Python program to split a string at uppercase letters.
import re
def task8(s):
    return re.findall(r'[A-Z][a-z]*', s)

print(task8("HelloWorldPythonExample"))
#  ['Hello', 'World', 'Python', 'Example']

Ex:9
#Write a Python program to insert spaces between words starting with capital letters.
import re
def task9(s):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', s)

print(task9("HelloWorldPythonExample"))
#  Hello World Python Example

Ex:10
#Write a Python program to convert a given camel case string to snake case.
import re
def task10(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

print(task10("helloWorldExample"))
#  hello_world_example
