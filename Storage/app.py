from operator import truediv
import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from expense import Expense
from income import Income
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json
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

conf_data = app_config["datastore"]
# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())


# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"mysql+pymysql://{conf_data['user']}:{conf_data['password']}@{conf_data['hostname']}:{conf_data['port']}/{conf_data['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"Connecting to DB. Hostname:{conf_data['hostname']}, Port: {conf_data['port']}")


def outputInfoLog(trace_id, event_name):
    msg = f"Stored event {event_name} request with a trace id of {trace_id}"
    logger.info(msg)


def getIncome(timestamp):
    """ Gets income records after the timestamp """
    session = DB_SESSION()
    
    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    records = session.query(Income).filter(Income.date_created > timestamp)
    
    results_list = []

    for record in records:
        results_list.append(record.to_dict())
    
    session.close()
    logger.info("Query for income records after %s returns %d results" % (timestamp, len(results_list)))
    
    return results_list, 200


def getExpense(timestamp):
    """ Gets expense records after the timestamp """
    session = DB_SESSION()
    
    # timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    records = session.query(Expense).filter(Expense.date_created > timestamp)
    
    results_list = []

    for record in records:
        results_list.append(record.to_dict())
    
    session.close()
    logger.info("Query for expense records after %s returns %d results" % (timestamp, len(results_list)))
    
    return results_list, 200

def process_messages():
    """ Process event messages """
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
    
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        # payload = msg["payload"]
        payload = json.loads(msg["payload"])
        
        if msg["type"] == "income":
            # Store the event1 (i.e., the payload) to the DB
           
            session = DB_SESSION()
     
            data = Income(payload['user_id'],
                           payload['earnings'],
                           payload['deducations'],
                           payload['income_category'],
                           payload['income_note'],
                           payload['timestamp'],
                           payload['trace_id'])

            session.add(data)

            session.commit()
            session.close()
            outputInfoLog(payload['trace_id'], 'addIncome')
        
        elif msg["type"] == "expense":
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()

            data = Expense(payload['user_id'],
                           payload['expense'],
                           payload['tax'],
                           payload['expense_category'],
                           payload['expense_note'],
                           payload['timestamp'],
                           payload['trace_id'])

            session.add(data)

            session.commit()
            session.close()

            outputInfoLog(payload['trace_id'], 'addExpense')

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)