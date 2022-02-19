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
          DROP TABLE expense
          ''')
db_cursor.execute('''
          DROP TABLE income
          ''')

db_conn.commit()
db_conn.close()
