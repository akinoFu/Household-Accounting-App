import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE expense
          (id INTEGER PRIMARY KEY ASC, 
           user_id VARCHAR(250) NOT NULL,
           expense FLOAT NOT NULL,
           tax FLOAT NOT NULL,
           expense_category VARCHAR(250) NOT NULL,
           expense_note VARHAR(500) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id varchar(250) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE income
          (id INTEGER PRIMARY KEY ASC, 
           user_id VARCHAR(250) NOT NULL,
           earnings FLOAT NOT NULL,
           deducations FLOAT NOT NULL,
           income_category VARCHAR(250) NOT NULL,
           income_note VARHAR(500) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id varchar(250) NOT NULL)
          ''')

conn.commit()
conn.close()
