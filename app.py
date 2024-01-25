from calendar import month_name
import calendar
from datetime import datetime
from functools import wraps
import locale
import secrets
import bcrypt
from flask import Flask, g, render_template, request, flash, redirect, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Engine, desc, extract, func, create_engine
from sqlalchemy.exc import SQLAlchemyError  
from decimal import Decimal 
from sqlalchemy.orm import sessionmaker


import os
from dotenv import load_dotenv
from flask_wtf import CSRFProtect

from models import Expense, Role, StoreTransfer, Users, DailySales, PurchaseOrder
from database import db
from constants import expense_types, purchase_types, from_transfer_types, to_transfer_types, OWNER, MANAGER, EMPLOYEE, store_names
app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Configure SQLAlchemy with the loaded database URI and SSL certificate path
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl': {
            'ssl_ca': os.getenv('SSL_CERTIFICATE')
        }
    }
}

# Initialize the SQLAlchemy object
db.init_app(app)

# Create the SQLAlchemy engine (move this within the application context)
with app.app_context():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)

# Generate a random secret key
secret_key = secrets.token_hex(24)
app.secret_key = secret_key


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, user_role):
        self.id = user_id
        self.user_role = user_role


# Custom decorator to restrict access to owners
def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' in session:
            user = Users.query.filter_by(email=session['user_email']).first()
            if user and user.user_role == 'Owner':
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return decorated_function

# Custom decorator to restrict access to managers
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' in session:
            user = Users.query.filter_by(email=session['user_email']).first()
            if user and user.user_role == 'Manager':
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return decorated_function

# Custom decorator to restrict access to employees
def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' in session:
            user = Users.query.filter_by(email=session['user_email']).first()
            if user and user.user_role == 'Employee':
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return decorated_function


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role')

        # Check if the user already exists in the database
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already in use. Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password before storing it in the database (assuming you have bcrypt set up)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create the new user with the assigned role
        new_user = Users(name=name, email=email, password=hashed_password, user_role=selected_role)

        # Add the user to the database and commit the transaction
        db.session.add(new_user)
        db.session.commit()

        flash('User registration successful!', 'success')
        return redirect(url_for('login'))

    roles = [EMPLOYEE, MANAGER, OWNER]  # List of available roles
    return render_template('signup.html', roles=roles)  # Pass roles to the template

@login_manager.user_loader
def load_user(user_id):
    # Query the user from the database based on user_id
    user = Users.query.get(int(user_id))
    if user:
        return User(user.id, user.user_role)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the user from the database using the provided email
        user = Users.query.filter_by(email=email).first()

        if user:
            # Check if the provided password matches the hashed password in the database
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                session['user_email'] = user.email  # Store the user's email in the session
                
                # Convert user's role from string to integer
                if user.user_role == 'Owner':
                    session['user_role'] = OWNER
                elif user.user_role == 'Manager':
                    session['user_role'] = MANAGER
                else:
                    session['user_role'] = EMPLOYEE

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  # Redirect to dashboard upon successful login

            else:
                flash('Login failed. Please check your credentials.', 'danger')
        else:
            flash('User not found. Please check your credentials.', 'danger')

    return render_template('login.html')

def is_logged_in():
    return 'user_id' in session

@app.context_processor
def utility_processor():
    def is_logged_in():
        return 'user_email' in session  # Check if user_email is in the session
    return dict(is_logged_in=is_logged_in)

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))



@app.route('/')
def index():
    return render_template('index.html')

# Dashboard route accessible to both managers and employees
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', current_user=current_user)


@app.route('/dailysales', methods=['GET'])
def dailysales():
    # Retrieve the daily sales data from the database
    daily_sales_data = DailySales.query.all()  # You may need to adjust this query based on your needs

    return render_template('dailysales.html', daily_sales_data=daily_sales_data)

@app.route('/dailysales', methods=['GET', 'POST'])
def dailysales_submit():
    if request.method == 'POST':
        try:
            # Utility function to convert input data or use default value
            def validate_or_default(value, default, data_type):
                try:
                    return data_type(value) if value else default
                except ValueError:
                    return default
            
            
            overwrite = request.form.get('overwrite') == 'on'

            # Retrieve and validate form data
            date = request.form.get('date')
            name_employee = request.form.get('name_employee')
            hours_employee = validate_or_default(request.form.get('hours_employee'), None, float)
            name_employee1 = request.form.get('name_employee1')
            hours_employee1 = validate_or_default(request.form.get('hours_employee1'), None, float)
            name_employee2 = request.form.get('name_employee2')
            hours_employee2 = validate_or_default(request.form.get('hours_employee2'), None, float)
            total_sales_shift1 = validate_or_default(request.form.get('total_sales_shift1'), None, float)
            total_sales_shift2 = validate_or_default(request.form.get('total_sales_shift2'), None, float)
            card_total_shift1 = validate_or_default(request.form.get('card_total_shift1'), None, float)
            card_total_shift2 = validate_or_default(request.form.get('card_total_shift2'), None, float)
            drop_total_shift1 = validate_or_default(request.form.get('drop_total_shift1'), None, float)
            drop_total_shift2 = validate_or_default(request.form.get('drop_total_shift2'), None, float)
            lotto_payout_shift1 = validate_or_default(request.form.get('lotto_payout_shift1'), None, float)
            lotto_payout_shift2 = validate_or_default(request.form.get('lotto_payout_shift2'), None, float)
            payout1_shift1 = validate_or_default(request.form.get('payout1_shift1'), None, float)
            payout1_shift2 = validate_or_default(request.form.get('payout1_shift2'), None, float)
            payout2_shift1 = validate_or_default(request.form.get('payout2_shift1'), None, float)
            payout2_shift2 = validate_or_default(request.form.get('payout2_shift2'), None, float)
            total_sales_day = validate_or_default(request.form.get('total_sales_day'), None, float)
            card_total_day = validate_or_default(request.form.get('card_total_day'), None, float)
            drop_total_day = validate_or_default(request.form.get('drop_total_day'), None, float)
            lotto_payout_day = validate_or_default(request.form.get('lotto_payout_day'), None, float)
            payout1_day = validate_or_default(request.form.get('payout1_day'), None, float)
            payout2_day = validate_or_default(request.form.get('payout2_day'), None, float)

            over_short = validate_or_default(request.form.get('over_short'), None, float)

            # Check if entry for the same date already exists
            existing_entry = DailySales.query.filter_by(date=date).first()

            if existing_entry and not overwrite:
                # If an entry for the same date exists and overwrite is not checked, warn the user
                flash('An entry for this date already exists. Check the overwrite box if you want to overwrite it.', 'warning')
                return redirect(url_for('dailysales'))

            if existing_entry and overwrite:
                # Overwrite the existing entry
                existing_entry.name_employee = name_employee
                existing_entry.hours_employee = hours_employee
                existing_entry.name_employee1=name_employee1,
                existing_entry.hours_employee1=hours_employee1,
                existing_entry.name_employee2=name_employee2,
                existing_entry.hours_employee2=hours_employee2,
                existing_entry.total_sales_shift1=total_sales_shift1,
                existing_entry.total_sales_shift2=total_sales_shift2,
                existing_entry.card_total_shift1=card_total_shift1,
                existing_entry.card_total_shift2=card_total_shift2,
                existing_entry.drop_total_shift1=drop_total_shift1,
                existing_entry.drop_total_shift2=drop_total_shift2,
                existing_entry.lotto_payout_shift1=lotto_payout_shift1,
                existing_entry.lotto_payout_shift2=lotto_payout_shift2,
                existing_entry.payout1_shift1=payout1_shift1,
                existing_entry.payout1_shift2=payout1_shift2,
                existing_entry.payout2_shift1=payout2_shift1,
                existing_entry.payout2_shift2=payout2_shift2,
                existing_entry.total_sales_day = total_sales_day,
                existing_entry.card_total_day = card_total_day,
                existing_entry.drop_total_day = drop_total_day,
                existing_entry.lotto_payout_day = lotto_payout_day,
                existing_entry.payout1_day = payout1_day,
                existing_entry.payout2_day = payout2_day,
                existing_entry.over_short=over_short               
                db.session.commit()
                flash('Entry for this date was successfully overwritten.', 'success')
            else:
                daily_sales_entry = DailySales(
                    date=date,
                    name_employee=name_employee,
                    hours_employee=hours_employee,
                    name_employee1=name_employee1,
                    hours_employee1=hours_employee1,
                    name_employee2=name_employee2,
                    hours_employee2=hours_employee2,
                    total_sales_shift1=total_sales_shift1,
                    total_sales_shift2=total_sales_shift2,
                    card_total_shift1=card_total_shift1,
                    card_total_shift2=card_total_shift2,
                    drop_total_shift1=drop_total_shift1,
                    drop_total_shift2=drop_total_shift2,
                    lotto_payout_shift1=lotto_payout_shift1,
                    lotto_payout_shift2=lotto_payout_shift2,
                    payout1_shift1=payout1_shift1,
                    payout1_shift2=payout1_shift2,
                    payout2_shift1=payout2_shift1,
                    payout2_shift2=payout2_shift2,
                    total_sales_day=total_sales_day,
                    card_total_day=card_total_day,
                    drop_total_day=drop_total_day,
                    lotto_payout_day=lotto_payout_day,
                    payout1_day=payout1_day,
                    payout2_day=payout2_day,
                    over_short=over_short
                )   
                db.session.add(daily_sales_entry)
                db.session.commit()
                flash('New entry was successfully added.', 'success')

        except SQLAlchemyError as e:
            # Handle database errors
            db.session.rollback()
            print(f"Database error: {e}")
            flash('There was an error processing your request.', 'error')

        # Redirect back to the dailysales page after processing
        return redirect(url_for('dailysales'))


@app.route('/store_transfer', methods=['GET', 'POST'])
def store_transfer():
    if request.method == 'POST':
        date = request.form.get('date')
        transfer_number = request.form.get('transfer_number')
        transferred_from = request.form.get('transferred_from')
        transferred_to = request.form.get('transferred_to')
        amount = request.form.get('amount')
        remark = request.form.get('remark')

        # Create a new StoreTransfer instance and add it to the database
        store_transfer = StoreTransfer(date=date, transfer_number=transfer_number, transferred_from=transferred_from, transferred_to=transferred_to, amount=amount, remark=remark)
        db.session.add(store_transfer)
        db.session.commit()
        flash("Store Transfer added successfully.", "success")

    # Retrieve existing transfers from the database
    transfers = StoreTransfer.query.order_by(StoreTransfer.date.desc()).all()

    return render_template(
        'store_transfer.html', 
        transfers=transfers, 
        from_transfer_types=from_transfer_types, 
        to_transfer_types=to_transfer_types,
        store_names=store_names  # Pass store_names to the template
    )



# Define the expenses function for handling the /expenses route
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        expense_date = request.form.get('expense_date')
        expense_type = request.form.get('expense_type')
        expense_description = request.form.get('expense_description')
        expense_amount = request.form.get('expense_amount')
        expense_pay_type = request.form.get('expense_pay_type')

        # Check if the expense_type is in the allowed expense types
        if expense_type not in expense_types:
            flash("Invalid expense type.", "error")
            return redirect(url_for('expenses'))

        new_expense = Expense(
            expense_date=expense_date,
            expense_type=expense_type,
            expense_description=expense_description,
            expense_amount=expense_amount,
            expense_pay_type=expense_pay_type
        )

        db.session.add(new_expense)
        db.session.commit()

        flash("Expense added successfully.", "success")
        return redirect(url_for('expenses'))

    expenses = Expense.query.order_by(desc(Expense.expense_date)).limit(100).all()

    return render_template('expenses.html', expenses=expenses, expense_types=expense_types)

@app.route('/purchase_order', methods=['GET', 'POST'])
def purchase_order():
    if request.method == 'POST':
        date = request.form.get('date')
        po_number = request.form.get('po_number')
        vendor_name = request.form.get('vendor_name')
        invoice_total = request.form.get('invoice_total')
        payment_method = request.form.get('payment_method')
        received_by = request.form.get('received_by')

        new_purchase_order = PurchaseOrder(
            date=date,
            po_number=po_number,
            vendor_name=vendor_name,
            invoice_total=invoice_total,
            payment_method=payment_method,
            received_by=received_by
        )

        db.session.add(new_purchase_order)
        db.session.commit()

        flash("Purchase order added successfully.", "success")
        return redirect(url_for('purchase_order'))

    purchase_order = PurchaseOrder.query.order_by(desc(PurchaseOrder.date)).limit(100).all()

    return render_template('purchase_order.html', purchase_order=purchase_order)

@app.route('/employee')
def employee():
    return render_template('employee.html')

@app.route('/main_terminal')
@manager_required
def main_terminal():
    return render_template('main_terminal.html')


@app.route('/misc')
def misc():
    return "Hello World"

@app.route('/lottery_input')
def lottery_input():
    return render_template('lottery_input.html')







## This is for the tpurchase_order fields##
def get_total_monthly_purchases(selected_month, selected_year):
    # Calculate total purchases for the selected month and year
    total_purchases = db.session.query(func.sum(PurchaseOrder.invoice_total)).filter(
        func.extract('year', PurchaseOrder.date) == selected_year,
        func.extract('month', PurchaseOrder.date) == selected_month
    ).scalar() or Decimal('0.0')

    return total_purchases

def get_purchases_by_payment_type(selected_month, selected_year):
    # Initialize the dictionary with all payment types set to zero
    purchases_by_payment_type = {pt: Decimal('0.0') for pt in purchase_types}

    # Perform database query and calculations
    for payment_type in purchase_types:
        total_purchase_by_payment = db.session.query(func.sum(PurchaseOrder.invoice_total)).filter(
            PurchaseOrder.payment_method == payment_type,
            func.extract('year', PurchaseOrder.date) == selected_year,
            func.extract('month', PurchaseOrder.date) == selected_month
        ).scalar() or Decimal('0.0')
        
        purchases_by_payment_type[payment_type] = total_purchase_by_payment

    return purchases_by_payment_type

def get_purchases_by_vendor(selected_month, selected_year):
    # Retrieve vendors and their total purchases, and total purchases by payment method
    vendors_and_purchases = db.session.query(
        PurchaseOrder.vendor_name,
        PurchaseOrder.payment_method,
        func.sum(PurchaseOrder.invoice_total)
    ).filter(
        func.extract('year', PurchaseOrder.date) == selected_year,
        func.extract('month', PurchaseOrder.date) == selected_month
    ).group_by(PurchaseOrder.vendor_name, PurchaseOrder.payment_method).all()

    # Initialize vendor purchases with all payment types set to zero
    vendor_purchases = {}
    for vendor, payment_method, total in vendors_and_purchases:
        if vendor not in vendor_purchases:
            # Initialize with zero totals for each payment type
            vendor_purchases[vendor] = {'total_purchase': Decimal('0.0')}
            for pt in purchase_types:
                vendor_purchases[vendor][pt] = Decimal('0.0')
        
        # Add totals to the respective payment method and to the total purchase
        if payment_method in purchase_types:  # Ensure the payment method is in your list
            vendor_purchases[vendor][payment_method] += total
        vendor_purchases[vendor]['total_purchase'] += total

    # Convert to list of dictionaries for easier template processing
    vendor_purchases_list = [
        {
            'vendor_name': vendor,
            'total_purchase': f"${totals['total_purchase']:.2f}",
            **{pt: f'${totals[pt]:.2f}' for pt in purchase_types}  # Include each payment type's total
        } for vendor, totals in vendor_purchases.items()
    ]

    return vendor_purchases_list

@app.route('/tpurchase_order', methods=['GET', 'POST'])
def tpurchase_order():
    if request.method == 'POST':
        selected_month = int(request.form['selected_month'])
        selected_year = int(request.form['selected_year'])

        # Calculate total monthly purchases
        total_monthly_purchases = get_total_monthly_purchases(selected_month, selected_year)

        # Calculate total purchases by payment type
        purchases_by_payment_type = get_purchases_by_payment_type(selected_month, selected_year)

        # Calculate total purchases by vendor
        vendor_purchases = get_purchases_by_vendor(selected_month, selected_year)

        data = {
            'total_monthly_purchases': f'${total_monthly_purchases}',
            'purchases_by_payment_type': purchases_by_payment_type,
            'vendor_purchases': vendor_purchases,
            'purchase_types': purchase_types  # pass purchase_types to your template
        }

        return render_template('tpurchase_order.html', **data)

    # Initial load or no POST request
    return render_template('tpurchase_order.html',
                           total_monthly_purchases='$0.00',
                           purchases_by_payment_type={},
                           vendor_purchases=[],
                           purchase_types=purchase_types)  # pass purchase_types to your template


## This is from the texpenses fields ##
def get_total_monthly_expenses(selected_month, selected_year):
    # Calculate total expenses for the selected month and year
    total_expenses = db.session.query(func.sum(Expense.expense_amount)).filter(
        func.extract('year', Expense.expense_date) == selected_year,
        func.extract('month', Expense.expense_date) == selected_month
    ).scalar() or Decimal('0.0')

    return total_expenses

def get_total_expenses_by_type(selected_month, selected_year):
    # Calculate total expenses by expense type for the selected month and year
    expenses_by_type = {}

    for expense_type in expense_types:
        total_expense_by_type = db.session.query(func.sum(Expense.expense_amount)).filter(
            func.extract('year', Expense.expense_date) == selected_year,
            func.extract('month', Expense.expense_date) == selected_month,
            Expense.expense_type == expense_type
        ).scalar() or Decimal('0.0')
        
        expenses_by_type[expense_type] = total_expense_by_type

    return expenses_by_type

def get_expenses_by_payment_type(selected_month, selected_year):
    # Calculate total expenses by payment type for the selected month and year
    expenses_by_payment_type = {}

    for payment_type in purchase_types:
        total_expense_by_payment_type = db.session.query(func.sum(Expense.expense_amount)).filter(
            func.extract('year', Expense.expense_date) == selected_year,
            func.extract('month', Expense.expense_date) == selected_month,
            Expense.expense_pay_type == payment_type
        ).scalar() or Decimal('0.0')
        
        expenses_by_payment_type[payment_type] = total_expense_by_payment_type

    return expenses_by_payment_type

@app.route('/texpenses', methods=['GET', 'POST'])
def texpenses():
    if request.method == 'POST':
        # Handle form submission here if needed
        pass

    # Retrieve selected month and year from the request, or set defaults
    selected_month = request.form.get('selected_month', None)
    selected_year = request.form.get('selected_year', None)

    # Calculate total monthly expenses
    total_monthly_expenses = get_total_monthly_expenses(selected_month, selected_year)

    # Calculate total expenses by expense type for the selected month and year
    expenses_by_type = get_total_expenses_by_type(selected_month, selected_year)

    # Calculate total expenses by payment type for the selected month and year
    expenses_by_payment_type = get_expenses_by_payment_type(selected_month, selected_year)

    data = {
        'total_monthly_expenses': total_monthly_expenses,
        'expenses_by_type': expenses_by_type,
        'expenses_by_payment_type': expenses_by_payment_type
    }

    return render_template('texpenses.html', **data)



def calculate_total_transfers(selected_month, selected_year):
    # Use SQL queries to calculate total transfers between each store
    
    # Create a query using SQLAlchemy's ORM to calculate total transfers
    query = db.session.query(
        StoreTransfer.transferred_from,
        StoreTransfer.transferred_to,
        db.func.sum(StoreTransfer.amount).label('total_transfer')
    ).filter(
        db.func.extract('year', StoreTransfer.date) == selected_year,
        db.func.extract('month', StoreTransfer.date) == selected_month
    ).group_by(
        StoreTransfer.transferred_from,
        StoreTransfer.transferred_to
    )
    
    # Execute the query and return the results
    total_transfers = query.all()

    return total_transfers

def calculate_store_owes(total_transfers):
    store_owes = {}
    
    # Iterate through total_transfers
    for transfer in total_transfers:
        from_store = transfer.transferred_from
        to_store = transfer.transferred_to
        amount = transfer.total_transfer

        # Check if from_store and to_store are different
        if from_store != to_store:
            # If from_store doesn't exist in store_owes, create an entry
            if from_store not in store_owes:
                store_owes[from_store] = {}
            
            # If to_store doesn't exist in from_store's entry, create an entry
            if to_store not in store_owes[from_store]:
                store_owes[from_store][to_store] = 0
            
            # Increment the owed amount
            store_owes[from_store][to_store] += amount
            
            # If to_store doesn't exist in store_owes, create an entry
            if to_store not in store_owes:
                store_owes[to_store] = {}
            
            # If from_store doesn't exist in to_store's entry, create an entry
            if from_store not in store_owes[to_store]:
                store_owes[to_store][from_store] = 0
            
            # Decrement the owed amount for the reverse direction
            store_owes[to_store][from_store] -= amount

    return store_owes

@app.route('/tstore_transfer', methods=['GET', 'POST'])
def tstore_transfer():
    if request.method == 'POST':
        # Handle form submission here if needed (you can add form handling logic here)
        pass

    # Retrieve selected month and year from the request, or set defaults
    selected_month = request.form.get('selected_month', None)
    selected_year = request.form.get('selected_year', None)

    # Calculate total transfers for the selected month and year
    total_transfers = calculate_total_transfers(selected_month, selected_year)

    # Calculate store owes based on total transfers
    store_owes = calculate_store_owes(total_transfers)

    # Include the 'month_names' variable in the template context directly
    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_transfer_types': from_transfer_types,  # Define from_transfer_types as needed
        'to_transfer_types': to_transfer_types,  # Define to_transfer_types as needed
        'month_names': [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        'total_transfers': total_transfers,  # Pass total transfers to the template
        'store_owes': store_owes  # Pass store owes data to the template
    }

    return render_template('tstore_transfer.html', **context)




@app.route('/tdaily_sales', methods=['GET', 'POST'])
def tdaily_sales():
    # Generate month names
    month_names = [calendar.month_name[i] for i in range(1, 13)]
    current_month = datetime.now().month
    current_year = datetime.now().year

    if request.method == 'POST':
        selected_month = int(request.form.get('selected_month', current_month))
        selected_year = int(request.form.get('selected_year', current_year))
        daily_sales_data = DailySales.query.filter(
            db.func.extract('year', DailySales.date) == selected_year,
            db.func.extract('month', DailySales.date) == selected_month
        ).order_by(DailySales.date).all()
    else:
        selected_month = current_month
        selected_year = current_year
        daily_sales_data = []

    return render_template(
        'tdaily_sales.html', 
        daily_sales_data=daily_sales_data,
        selected_month=selected_month,
        selected_year=selected_year,
        month_names=month_names
    )


if __name__ == '__main__':
    app.run(debug=True)

