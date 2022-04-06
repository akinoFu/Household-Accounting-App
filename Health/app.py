from ast import Try
from ssl import SSLSocket
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
import uuid
from flask_cors import CORS, cross_origin
import os
from pathlib import Path
import json

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

HEALTH_FILE = app_config["datastore"]["filename"]


def getHealth():
    """ Return health check resutls"""
    trace_id = str(uuid.uuid4())
    logger.info(f"getHealth: Getting the check restuls from json file (ID: {trace_id})")
    
    listObj = []
    with open(HEALTH_FILE) as fh:
        listObj = json.load(fh)
    latest_health = listObj[-1]
    
    logger.info(f"getHealth: Successfully got the check restuls from json file (ID: {trace_id}) - {latest_health}")
    
    time_elapses = datetime.datetime.now() - datetime.datetime.strptime(latest_health["last_update"], "%Y-%m-%dT%H:%M:%S.%fZ")
    latest_health["last_update"] = f"{time_elapses.seconds} seconds ago"
    
    return latest_health, 200


def checkHealth(svc):
    try:
        res = requests.get(app_config["eventstore"][svc] + "/health", timeout=app_config["eventstore"]["timeout"])
        return "Running" if res.status_code == 200 else "Down"
    except:
        return "Down"


def populate_health():
    """ Periodically stores health check restuls """
    trace_id = str(uuid.uuid4())
    logger.info(f"Start Periodic Health Check (ID: {trace_id})")

    # Get health check
    health = {}
    health["receiver"] = checkHealth("receiver")
    health["storage"] = checkHealth("storage")
    health["processing"] = checkHealth("processing")
    health["audit"] = checkHealth("audit")
    health["last_update"] = datetime.datetime.now().strftime( "%Y-%m-%dT%H:%M:%S.%fZ")

    logger.info(f"Health check ends (ID: {trace_id}) - {health}")

    # Store the dataset into the json file
    listObj = []
    with open(HEALTH_FILE) as fh:
        listObj = json.load(fh)

    with open(HEALTH_FILE, "w") as fh:
        listObj.append(health)

        if len(listObj) > app_config["datastore"]["max"]:
            del listObj[0]

        json.dump(listObj, fh, indent=2)
    
    logger.info(f"Successfully stored the health check restul (ID: {trace_id})")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)