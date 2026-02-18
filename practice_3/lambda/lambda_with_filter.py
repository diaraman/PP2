numbers = [1, 2, 3, 4, 5]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)


ages = [12, 18, 25, 15]
adults = list(filter(lambda x: x >= 18, ages))
print(adults)


words = ["apple", "bat", "banana"]
long_words = list(filter(lambda x: len(x) > 3, words))
print(long_words)