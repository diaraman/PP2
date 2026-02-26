## 1.py
Subtracts 5 days from the current date/time.

```python
from datetime import datetime, timedelta

today = datetime.now()
new_date = today - timedelta(days=5)

print("Today:", today)
print("5 days ago:", new_date)
```

## 2.py
Shows yesterday, today, and tomorrow.

```python
from datetime import datetime, timedelta
today=datetime.now()
yesterday=today-timedelta(days=1)
tomorrow=today+timedelta(days=1)
print("Today", today)
print("Yesterday", yesterday)
print("Tomorrow", tomorrow)
```

## 3.py
Removes microseconds from `datetime.now()` for cleaner output.

```python
from datetime import datetime

now = datetime.now()
no_micro = now.replace(microsecond=0)

print("With microseconds:", now)
print("Without microseconds:", no_micro)
```

## 4.py
Calculates the difference between two dates in seconds.

```python
from datetime import datetime

date1 = datetime(2026, 2, 20, 10, 0, 0)
date2 = datetime(2026, 2, 25, 12, 0, 0)

difference = date2 - date1
seconds = difference.total_seconds()

print("Seconds difference:", seconds)
```
