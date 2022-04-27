from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base

class Stats(Base):
    """ Stats """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_income_records = Column(Integer, nullable=True)
    num_expense_records =Column(Integer, nullable=True)
    total_income = Column(Float, nullable=False)
    total_expense =Column(Float, nullable=False)
    income_last_updated = Column(DateTime, nullable=False)
    expense_last_updated = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    
    def __init__(self, num_income_records, num_expense_records, total_income, total_expense, income_last_updated, expense_last_updated, last_updated):
        """ Initializes an income reading """
        self.num_income_records = num_income_records
        self.num_expense_records = num_expense_records
        self.total_income = total_income
        self.total_expense = total_expense
        self.income_last_updated = income_last_updated
        self.expense_last_updated = expense_last_updated
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of an income reading """
        dict = {}
        dict['num_income_records'] = self.num_income_records
        dict['num_expense_records'] = self.num_expense_records
        dict['total_income'] = self.total_income
        dict['total_expense'] = self.total_expense
        dict['income_last_updated'] = self.income_last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        dict['expense_last_updated'] = self.expense_last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return dict
