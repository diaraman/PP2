n = int(input())

i = 1
total = 0
while i <= n:
    if i % 2 == 0:
        i += 1
        continue
    total += i
    i += 1

print(total) #it calculates the sum of all odd integers from 1 to n