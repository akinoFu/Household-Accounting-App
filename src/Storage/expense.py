from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base
import datetime


class Expense(Base):
    """ Expense """

    __tablename__ = "expense"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    expense = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    expense_category = Column(String(250), nullable=False)
    expense_note = Column(String(500), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)
    
    def __init__(self, user_id, expense, tax, expense_category, expense_note, timestamp, trace_id):
        """ Initializes an income reading """
        self.user_id = user_id
        self.expense = expense
        self.tax = tax
        self.expense_category = expense_category
        self.expense_note = expense_note
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ") # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of an income reading """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['expense'] = self.expense
        dict['tax'] = self.tax
        dict['expense_category'] = self.expense_category
        dict['expense_note'] = self.expense_note
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
