from urllib import request
import connexion
from connexion import NoContent
import json
from datetime import datetime
import requests
import logging
import logging.config
import yaml
import uuid
import datetime
from pykafka import KafkaClient
import time
import os

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

HEADER = { "Content-Type" : "application/json" }

# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
retry_num = app_config["events"]["retry_num"]
for i in range(retry_num):
    try:
        logger.info(f"Trying to connect to Kafka...{i}")
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        logger.info("Connected to Kafka successfully")
        break
    except:
        logger.info("The connection to Kafka failed")
        time.sleep(3)

def getHealth():
    """ Return 200 for health check"""
    return NoContent, 200
    
def outputInfoLog(trace_id, event_name, status_code):
    msg = f"Returned event {event_name} response (Id: {trace_id}) with status {status_code}"
    logger.info(msg)


def addIncome(body):
    """ Receives an adding income event """
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    # r = requests.post(f"{app_config['eventstore1']['url']}", data=json.dumps(body), headers=HEADER)
    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "income",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "payload": json.dumps(body) }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    outputInfoLog(trace_id, "addIncome", 201)

    return NoContent, 201


def addExpense(body):
    """ Receives an adding expense event """
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id 
    # r = requests.post(f"{app_config['eventstore2']['url']}", data=json.dumps(body), headers=HEADER)
    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "expense",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "payload": json.dumps(body) }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    outputInfoLog(trace_id,"addExpense", 201)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
# app.run(port=8080, debug=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)