from datetime import date
from pickle import dump

start_date = date(2024, 3, 5)

file = open('start_date.pkl', 'wb')
dump(start_date, file)
file.close()
