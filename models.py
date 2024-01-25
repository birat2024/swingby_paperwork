
from sqlalchemy import DATETIME, DECIMAL, Column, Date, Float, Integer, String
from database import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship  # Import relationship

from constants import OWNER, MANAGER, EMPLOYEE



class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Integer, nullable=False, default=EMPLOYEE)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False)  # Assign a numerical level to each role


class StoreTransfer(db.Model):
    __tablename__ = 'store_transfer'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transfer_number = db.Column(db.String(255), nullable=False)
    transferred_from = db.Column(db.String(255), nullable=False)
    transferred_to = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    remark = db.Column(db.String(255))

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.Date, nullable=False)
    expense_type = db.Column(db.String(255), nullable=False)
    expense_description = db.Column(db.Text, nullable=False)
    expense_amount = db.Column(db.Float, nullable=False)
    expense_pay_type = db.Column(db.String(255), nullable=False)

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATETIME)
    po_number = Column(String(20))
    vendor_name = Column(String(100))
    invoice_total = Column(DECIMAL(10, 2))
    payment_method = Column(String(50))
    received_by = Column(String(100))


class DailySales(db.Model):
    __tablename__ = 'daily_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name_employee = db.Column(db.String(255))
    hours_employee = db.Column(db.Float)
    name_employee1 = db.Column(db.String(255))
    hours_employee1 = db.Column(db.Float)
    name_employee2 = db.Column(db.String(255))
    hours_employee2 = db.Column(db.Float)
    total_sales_shift1 = db.Column(db.Float, nullable=False)
    total_sales_shift2 = db.Column(db.Float)
    card_total_shift1 = db.Column(db.Float)
    card_total_shift2 = db.Column(db.Float)
    drop_total_shift1 = db.Column(db.Float)
    drop_total_shift2 = db.Column(db.Float)
    lotto_payout_shift1 = db.Column(db.Float)
    lotto_payout_shift2 = db.Column(db.Float)
    payout1_shift1 = db.Column(db.Float)
    payout1_shift2 = db.Column(db.Float)
    payout2_shift1 = db.Column(db.Float)
    payout2_shift2 = db.Column(db.Float)
    over_short = db.Column(db.Float)
    total_sales_day = db.Column(db.Float, nullable=False)
    card_total_day = db.Column(db.Float)
    drop_total_day = db.Column(db.Float)
    lotto_payout_day = db.Column(db.Float)
    payout1_day = db.Column(db.Float)
    payout2_day = db.Column(db.Float)
