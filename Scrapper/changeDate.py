from datetime import date
from pickle import dump

start_date = date(2024, 4, 30)

file = open('start_date.pkl', 'wb')
dump(start_date, file)
file.close()
