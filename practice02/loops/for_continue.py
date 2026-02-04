nums = list(map(int, input().split()))

product = 1
found = False

for num in nums:
    if num % 2 != 0:
        continue
    else:
        product *= num
        found = True

print(product if found else 0) #it calculates the multiplication of all even numbers in the list; returns 0 if no even numbers are found