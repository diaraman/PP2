# Iterator and generator exercises
mystr = "banana"
myit = iter(mystr)

print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
#2
#Create a generator that generates the squares of numbers up to some number N
def sq(n):
    for i in range (1,n+1):
        yield i*i
n=int(input())

for i in sq(n):
    print(i,end=" ")
