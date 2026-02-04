i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

i = -5
while i < 10:
    if i == 0: # we skip 0 to avoid ZeroDivisionError
        continue
    print(1 / i)
    i += 1