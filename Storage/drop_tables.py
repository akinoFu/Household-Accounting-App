import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE expense
          ''')
c.execute('''
          DROP TABLE income
          ''')
conn.commit()
conn.close()
