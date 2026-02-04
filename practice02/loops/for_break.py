nums = list(map(int, input().split()))

index = -1
for i in range(len(nums)):
    if nums[i] < 0:
        index = i
        break

print(index) #it finds the index of the first negative number in the list