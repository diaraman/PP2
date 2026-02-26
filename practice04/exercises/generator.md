## 1.py
Generates squares from `1` to `N`.

```python
def square(N):
    for i in range(1, N+1):
        yield i**2
N=int(input())
print(*square(N))
```

## 2.py
Prints all even numbers from `0` to `n`, separated by commas.

```python
def evens(n):
    for i in range(n+1):
        if i%2==0:
            yield i
n=int(input())
print(",".join(map(str, evens(n))))
```

## 3.py
Yields numbers divisible by `12` up to `n`.

```python
def a(n):
    for i in range(1, n+1):
        if i%12==0:
            yield i
n=int(input())
print(*a(n))
```

## 4.py
Generates squares for every number in the given range `[a, b]`.

```python
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

a, b = map(int, input().split())
for val in squares(a, b):
    print(val)
```

## 5.py
A countdown generator from `n` to `0`.

```python
def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input())
print(*countdown(n))
```
