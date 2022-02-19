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

HEADER = { "Content-Type" : "application/json" }

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def outputInfoLog(trace_id, event_name, status_code):
    msg = f"Returned event {event_name} response (Id: {trace_id}) with status {status_code}"
    logger.info(msg)


def addIncome(body):
    """ Receives an adding income event """
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    # r = requests.post(f"{app_config['eventstore1']['url']}", data=json.dumps(body), headers=HEADER)
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "bp",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
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
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "bp",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": json.dumps(body) }
    msg_str = json.dumps(msg)

    outputInfoLog(trace_id,"addExpense", 201)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
# app.run(port=8080, debug=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)