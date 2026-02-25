# Date and time operations
import datetime

x = datetime.datetime.now()

print(x.year)
print(x.strftime("%A"))
# 2 
import datetime

x = datetime.datetime(2018, 6, 1)

print(x.strftime("%B"))
