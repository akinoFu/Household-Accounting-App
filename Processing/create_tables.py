import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE stats
          (id INTEGER PRIMARY KEY ASC, 
           num_income_records INTEGER NOT NULL,
           num_expense_records INTEGER NOT NULL,
           total_income FLOAT NOT NULL,
           total_expense FLOAT NOT NULL,
           income_last_updated VARCHAR(100) NOT NULL,
           expense_last_updated VARCHAR(100) NOT NULL,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
