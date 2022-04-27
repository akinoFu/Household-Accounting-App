import mysql.connector
import yaml

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

hostname= app_config["datastore"]["hostname"]
mysqluser= app_config["datastore"]["user"]
mysqlpswd= app_config["datastore"]["password"]
db = app_config["datastore"]["db"]

db_conn = mysql.connector.connect(host=hostname, user=mysqluser, password=mysqlpswd, database=db)

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE expense
          (id INT NOT NULL AUTO_INCREMENT, 
           user_id VARCHAR(250) NOT NULL,
           expense DECIMAL(10,2) NOT NULL,
           tax DECIMAL(10,2) NOT NULL,
           expense_category VARCHAR(250) NOT NULL,
           expense_note VARCHAR(500) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT expense_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE income
          (id INT NOT NULL AUTO_INCREMENT, 
           user_id VARCHAR(250) NOT NULL,
           earnings DECIMAL(10,2) NOT NULL,
           deducations DECIMAL(10,2) NOT NULL,
           income_category VARCHAR(250) NOT NULL,
           income_note VARCHAR(500) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT income_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
