from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base
import datetime


class Income(Base):
    """ Income """

    __tablename__ = "income"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    earnings = Column(Float, nullable=False)
    deducations = Column(Float, nullable=False)
    income_category = Column(String(250), nullable=False)
    income_note = Column(String(500), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)
    
    def __init__(self, user_id, earnings, deducations, income_category, income_note, timestamp, trace_id):
        """ Initializes an income reading """
        self.user_id = user_id
        self.earnings = earnings
        self.deducations = deducations
        self.income_category = income_category
        self.income_note = income_note
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of an income reading """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['earnings'] = self.earnings
        dict['deducations'] = self.deducations
        dict['income_category'] = self.income_category
        dict['income_note'] = self.income_note
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
