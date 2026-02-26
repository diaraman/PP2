# Iterator example
class CountToThree:
    def __init__(self):
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 3:
            value = self.current
            self.current += 1
            return value
        raise StopIteration


print("Iterator:")
for number in CountToThree():
    print(number)


# Generator example
def squares(items):
    for item in items:
        yield item * item


print("Generator:")
n = [1, 2, 3, 4]
for value in squares(n):
    print(value)
