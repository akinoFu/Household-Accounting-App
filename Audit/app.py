import connexion
from connexion import NoContent
import json
import logging
import logging.config
import yaml
from pykafka import KafkaClient

HEADER = { "Content-Type" : "application/json" }

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def getIncome(index):
    """ Get Inome record in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving Income at index %d" % index)
    
    try:
        for i, msg in enumerate(consumer):
            if i == index:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                result = json.loads(msg["payload"])
                return result, 200
            
    except:
        logger.error("No more messages found")

    logger.error("Could not find Income at index %d" % index)
    return { "message": "Not Found"}, 404


def getExpense(index):
    """ Get Expense record in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving Expense at index %d" % index)
    
    try:
        for i, msg in enumerate(consumer):
            if i == index:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                result = json.loads(msg["payload"])
                return result, 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find Expense at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
# app.run(port=8080, debug=True)

if __name__ == "__main__":
    app.run(port=8110, debug=True)