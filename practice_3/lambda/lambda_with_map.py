numbers = [1, 2, 3]
squares = list(map(lambda x: x * x, numbers))
print(squares)



names = ["alice", "bob"]
capitalized = list(map(lambda x: x.capitalize(), names))
print(capitalized)



temps_c = [0, 20, 30]
temps_f = list(map(lambda c: (c * 9/5) + 32, temps_c))
print(temps_f)