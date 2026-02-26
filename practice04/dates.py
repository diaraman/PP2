import datetime

now = datetime.datetime.now() # Current date and time.
print("Now:", now)

print("Day:", now.strftime("%A")) # Day name (Monday, Tuesday, ...).