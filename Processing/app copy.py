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

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def getStats():
    """ Get proccessed result """
    trace_id = str(uuid.uuid4())
    logger.info("Start Getting Statistics (ID: {trace_id})")
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

    last_updated = stats["last_updated"]
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # if "last_updated" in stats.keys():
    #     last_updated = stats["last_updated"]
    # else:
    #     last_updated = current_time

    response_income = requests.get(app_config["eventstore"]["url"] + "/income?timestamp=" + last_updated)
    response_expense = requests.get(app_config["eventstore"]["url"] + "/expense?timestamp=" + last_updated)

    if response_income.status_code == 200 and response_income.status_code == 200:
        count_income = len(response_income.json())
        count_expense = len(response_expense.json())

        income_latest_date = "1900-01-01T00:00:00.000Z"
        expense_latest_date = "1900-01-01T00:00:00.000Z"

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
            # if income_latest_date > expense_latest_date:
            #     last_updated = income_latest_date
            # else:
            #     last_updated = expense_latest_date

            new_stats = Stats(stats["num_income_records"],
                            stats["num_expense_records"],
                            stats["total_income"],
                            stats["total_expense"],
                            datetime.datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%fZ"))
                            # current_time)

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
            "last_updated": "1900-01-01T00:00:00.000Z"}


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)