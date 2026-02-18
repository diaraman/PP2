# Words to sort.
words = ["banana", "kiwi", "apple", "pear"]

# Sort by word length using a lambda key.
by_length = sorted(words, key=lambda word: len(word))

print(by_length)
