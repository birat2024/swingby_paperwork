
from datetime import date, datetime
from sqlalchemy import DATETIME, DECIMAL, Column, DateTime, Integer, String
from flask_login import UserMixin
from sqlalchemy.orm import relationship  

from database import db



ROLES = ['Employee', 'Manager', 'Owner']

class GlobalSettings(db.Model):
    __tablename__ = 'global_settings'

    id = db.Column(db.Integer, primary_key=True)
    default_timezone = db.Column(db.String(64))  # Assuming storing timezone as string
    # Add other settings fields as needed


user_roles_association = db.Table('user_roles_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(255), nullable=False)
    selected_store_id = db.Column(db.Integer)

    # Establishing the many-to-many relationship
    stores = db.relationship('Store', secondary='user_store_association', backref='users', lazy='dynamic')
    roles = db.relationship('Role', secondary=user_roles_association, backref=db.backref('users', lazy='dynamic'))



    # Add the is_active method required by Flask-Login
    def is_active(self):
        return True  # You can customize this based on your logic

    # Add any other methods or properties needed by Flask-Login

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False)  # Assign a numerical level to each role



class StoreTransfer(db.Model):
    __tablename__ = 'store_transfer'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transfer_number = db.Column(db.String(20), unique=True, nullable=False)
    transferred_from = db.Column(db.Integer, db.ForeignKey('store_name.id'), nullable=False)
    transferred_to = db.Column(db.Integer, db.ForeignKey('store_name.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    remark = db.Column(db.String(200))

    transferred_from_store = db.relationship('Store', foreign_keys=[transferred_from], backref='transfers_from')
    transferred_to_store = db.relationship('Store', foreign_keys=[transferred_to], backref='transfers_to')

class Store(db.Model):
    __tablename__ = 'store_name'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    expenses = db.relationship('Expense', back_populates='store', lazy=True)
    daily_sales = db.relationship('DailySales', back_populates='store', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', back_populates='store', lazy=True)
    lottery_entries = db.relationship('LotteryEntry', back_populates='store', lazy=True)
    day_lottery_entries = db.relationship('LotteryEntry', back_populates='store', lazy=True)
    financial_records = db.relationship('FinancialRecord', back_populates='store', lazy=True)
    store_transfers_from = db.relationship('StoreTransfer', foreign_keys=[StoreTransfer.transferred_from], backref='store_transfers_from', lazy=True)
    store_transfers_to = db.relationship('StoreTransfer', foreign_keys=[StoreTransfer.transferred_to], backref='store_transfers_to', lazy=True)

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_date = db.Column(db.Date)
    expense_type = db.Column(db.String(255))
    expense_description = db.Column(db.Text)
    expense_amount = db.Column(db.Numeric(10, 2))
    expense_pay_type = db.Column(db.String(255))

    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'))

    # Update the relationship to use the new backref name
    store = db.relationship('Store', backref='expense_records')


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATETIME)
    po_number = Column(String(20))
    vendor_name = Column(String(100))
    invoice_total = Column(DECIMAL(10, 2))
    payment_method = Column(String(50))
    received_by = Column(String(100))
    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'))

    store = db.relationship('Store', backref='purchase_order')


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
    bonus_for_day = db.Column(db.Boolean, default=False)
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
    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'))

  # Define a relationship with the Store model
    store = db.relationship('Store', backref='daily_sales_records')




class FinancialRecord(db.Model):
    __tablename__ = 'financial_records'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_revenue = db.Column(db.Numeric(10, 2), nullable=False)
    total_purchases = db.Column(db.Numeric(10, 2), nullable=False)
    total_expenses = db.Column(db.Numeric(10, 2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'), nullable=False)

    # Relationship with Store
    store = db.relationship('Store', back_populates='financial_records')



class LotteryEntry(db.Model):
    __tablename__ = 'lottery_entries'
    id = db.Column(db.Integer, primary_key=True)
    row_number_entry = db.Column(db.Integer)
    amount = db.Column(db.Numeric(10, 2))
    begin_day = db.Column(db.Integer)
    end_day = db.Column(db.Integer)
    sold = db.Column(db.Integer)
    total = db.Column(db.Numeric(10, 2))
    expense_date = db.Column(db.Date, default=date.today)
    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'), nullable=False)

    store = db.relationship('Store', backref='lottery_entries_records')

    def to_dict(self):
            """Convert model instance to dictionary."""
            return {
                'id': self.id,
                'row_number_entry': self.row_number_entry,
                'amount': str(self.amount),  # Convert decimal to string for JSON serialization
                'begin_day': self.begin_day,
                'end_day': self.end_day,
                'sold': self.sold,
                'total': str(self.total),  # Convert decimal to string
                'expense_date': self.expense_date.isoformat(),  # Convert date to string
                'store_id': self.store_id
            }

class DayLotteryEntry(db.Model):

    __tablename__ = 'day_lottery_entries'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store_name.id'), nullable=False)
    total_scratch_off = db.Column(db.Numeric(10, 2), nullable=False)
    total_online = db.Column(db.Numeric(10, 2), nullable=False)
    actual_total = db.Column(db.Numeric(10, 2), nullable=False)
    pos_sale = db.Column(db.Numeric(10, 2), nullable=False)
    over_short = db.Column(db.Numeric(10, 2), nullable=False)


    store = db.relationship('Store', backref='day_lottery_entries_records')