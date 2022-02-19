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



with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
conf_data = app_config["datastore"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def outputInfoLog(trace_id, event_name):
    msg = f"Stored event {event_name} request with a trace id of {trace_id}"
    logger.info(msg)


DB_ENGINE = create_engine(f"mysql+pymysql://{conf_data['user']}:{conf_data['password']}@{conf_data['hostname']}:{conf_data['port']}/{conf_data['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"Connecting to DB. Hostname:{conf_data['hostname']}, Port: {conf_data['port']}")

def addIncome(body):
    """ Receives an adding income event """
    print(conf_data['user'])
    session = DB_SESSION()

    bp = Income(body['user_id'],
                body['earnings'],
                body['deducations'],
                body['income_category'],
                body['income_note'],
                body['timestamp'],
                body['trace_id'])

    session.add(bp)

    session.commit()
    session.close()

    outputInfoLog(body['trace_id'], 'addIncome')
    return NoContent, 201


def addExpense(body):
    """ Receives an adding expense event """

    session = DB_SESSION()

    bp = Expense(body['user_id'],
                body['expense'],
                body['tax'],
                body['expense_category'],
                body['expense_note'],
                body['timestamp'],
                body['trace_id'])

    session.add(bp)

    session.commit()
    session.close()

    outputInfoLog(body['trace_id'], 'addExpense')

    return NoContent, 201

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


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090, debug=True)