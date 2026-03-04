import re
print("1:", re.findall(r"ab*", "ac abbc abbbc"))# 1. Match a string that has 'a' followed by zero or more 'b's
print("2:", re.findall(r"ab{2,3}", "ab abbc abbbc abbbbc")) # 2. Find 'a' followed 'b' that appears two or three times
print("3:", re.findall(r'[a-z]+_[a-z]+', 'hello_world foo_bar ABC')) # 3. Find sequences of lowercase letters joined with an underscore
print("4:", re.findall(r"[A-Z][a-z]+", 'Hello World foo Bar')) # 4. Find sequences of one uppercase letter followed by lowercase letters
match=re.search(r'a.*b', "axxb")
if match:
    print("5:", match.group())# 5. Match a string that has 'a' followed by anything, ending in 'b'
print("6:", re.sub(r'[.,]', ':', "hello.how are you,")) #Replace all occurrences of space, comma, or dot with a colon
def camelCase(s): 
    text=s.split("_")
    result=text[0]
    for i in text[1:]:
        result=result+i.capitalize()
    return result
print("7:", camelCase("hello_world_hi")) #7 from snake to camelcase
print("8:", re.split(r'(?=[A-Z])', "helloWorldHi")) #8 splits when it is capitalized
print("9:", re.sub(r'(?<=([a-z]))(?=[A-Z])', ' ', "HelloWorldHi")) #9 inserts spaces if there is a capitalized letter
def camel_to_snake(s):
    result = re.sub(r'([A-Z])', r'_\1', s)
    result = result.lower()
    if result.startswith('_'):
        result = result[1:]
    return result
print("10:", camel_to_snake("HelloWorldFoo"))# 10. Convert camelCase to snake_case
      
