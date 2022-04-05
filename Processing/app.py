import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from stats import Stats
from base import Base
import uuid
from flask_cors import CORS, cross_origin
import os
import sqlite3
from pathlib import Path

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# with open('app_conf.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def getStats():
    """ Get proccessed result """
    trace_id = str(uuid.uuid4())
    logger.info(f"Start Getting Statistics (ID: {trace_id})")
    session = DB_SESSION()
    record = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if record == None:
        logger.error(f"Statistics do not exist (ID: {trace_id})")
        return {"message": "Statistics do not exist"}, 404

    result = record.to_dict()
    logger.debug(f"Statistics {result} (ID: {trace_id})")
    logger.info(f"Complete Getting Statistics (ID: {trace_id})")
    
    return result, 200


def populate_stats():
    """ Periodically update stats """
    trace_id = str(uuid.uuid4())
    logger.info(f"Start Periodic Processing (ID: {trace_id})")

    stats = get_latest_processing_stats()

    income_latest_date = stats["income_last_updated"]
    expense_latest_date = stats["expense_last_updated"]

    response_income = requests.get(app_config["eventstore"]["url"] + "/income?timestamp=" + income_latest_date)
    response_expense = requests.get(app_config["eventstore"]["url"] + "/expense?timestamp=" + expense_latest_date)

    if response_income.status_code == 200 and response_income.status_code == 200:
        count_income = len(response_income.json())
        count_expense = len(response_expense.json())

        if count_income > 0:
            stats["num_income_records"] += len(response_income.json())
            
            for record in response_income.json():
                stats["total_income"] += record["earnings"]
                if income_latest_date < record['date_created']:
                    income_latest_date = record['date_created']

            
        if count_expense > 0:
            stats["num_expense_records"] += len(response_expense.json())
            for record in response_expense.json():
                stats["total_expense"] += record["expense"]
                if expense_latest_date < record['date_created']:
                    expense_latest_date = record['date_created']
            
        if count_income == 0 and count_expense == 0:
            logger.info(f"No Data Updated (ID: {trace_id})")
        else:
            new_stats = Stats(stats["num_income_records"],
                            stats["num_expense_records"],
                            stats["total_income"],
                            stats["total_expense"],
                            datetime.datetime.strptime(income_latest_date, "%Y-%m-%dT%H:%M:%S.%fZ"),
                            datetime.datetime.strptime(expense_latest_date, "%Y-%m-%dT%H:%M:%S.%fZ"),
                            datetime.datetime.now())

            session = DB_SESSION()
            session.add(new_stats)
            session.commit()
            session.close()

            logger.info(f"Finish Periodic Processing Successfully (ID: {trace_id})")

    else:
        logger.info(f"Periodic Processing Not Working (ID: {trace_id})")



def get_latest_processing_stats():
    """ Get the latest stats object, or None if there isn't one """
    session = DB_SESSION()

    results = session.query(Stats).order_by(Stats.last_updated.desc())
    
    session.close()

    if len(results.all()) > 0:
        return results.first().to_dict()
    
    return {"num_income_records": 0,
            "num_expense_records": 0,
            "total_income": 0,
            "total_expense": 0,
            "income_last_updated": "1900-01-01T00:00:00.000Z",
            "expense_last_updated": "1900-01-01T00:00:00.000Z",
            "last_updated": datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S.%fZ")}


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


def create_datastore():
    filepath = Path(app_config['datastore']['filename'])
    if filepath.is_file():
        logger.info(f"{filepath} exists")
    else:
        logger.info(f"{filepath} does not exist.")
        conn = sqlite3.connect(app_config['datastore']['filename'])
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
        logger.info(f"{filepath} created")



app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    create_datastore()
    init_scheduler()
    app.run(port=8100, use_reloader=False)