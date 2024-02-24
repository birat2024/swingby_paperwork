
import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
import logging
from math import ceil
import os

from flask import Flask, app, current_app, jsonify, render_template, request, flash, redirect, session, url_for
from flask_login import current_user, login_required, logout_user
import pytz
from sqlalchemy import and_, desc, extract, func, or_
from sqlalchemy.exc import SQLAlchemyError  
from sqlalchemy.orm import aliased

from decimal import Decimal 
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename




from auth import fetch_user_stores, get_selected_store_for_user, get_user_stores

from models import DayLotteryEntry, Expense, LotteryEntry, StoreTransfer, Users, DailySales, PurchaseOrder, Store, FinancialRecord, GlobalSettings
from database import db
from constants import expense_types, payment_types, from_transfer_types, to_transfer_types, store_names
from flask import Blueprint
from terminal.forms import DailySalesForm, DailySalesSubmitForm, DayLotteryEntryForm, EmployeeIntakeForm, ExpenseForm, LotteryForm, MonthlyLotteryStoreForm, MonthlyPaperworkForm, PurchaseOrderForm, ScheduleForm, ScheduleRetrievalForm, StoreTransferForm, TExpensesForm, TStoreTransferForm, TotalPurchaseOrderForm
from terminal.models import Schedule
from users.routes import employee_required, manager_required, owner_required


terminal = Blueprint('terminal', __name__)




@terminal.route('/dashboard', methods=['GET', 'POST'])
@employee_required
def dashboard():
    # Fetch the selected store using the utility function
    selected_store = get_selected_store_for_user(current_user)

    if request.method == 'POST':
        selected_store_id = request.form.get('selected_store')
        if selected_store_id is not None:
            try:
                selected_store_id = int(selected_store_id)
                selected_store = Store.query.get(selected_store_id)
            except ValueError:
                selected_store = None

            # Save the selected store in the session
            session['selected_store'] = selected_store.id if selected_store else None

    all_stores = Store.query.all()  # Fetch all available stores

    return render_template('dashboard.html', current_user=current_user, selected_store=selected_store, all_stores=all_stores)

#<----- Daily Sales ----->#


def Swingbyemployees():
    # Filter users where the role is either 'Employee' or 'Manager'
    employee_and_manager_users = Users.query.filter(Users.user_role.in_(['Employee', 'Manager', 'Owner'])).all()
    return employee_and_manager_users


@terminal.route('/dailysales', methods=['GET'])
@employee_required
def show_dailysales():
    user_stores, selected_store = fetch_user_stores(current_user)
    form = DailySalesSubmitForm()
    form.selected_store.choices = [(store.id, store.name) for store in user_stores]

    # Populate employee choices with a placeholder at the beginning
    employee_choices = [(user.id, user.name) for user in Swingbyemployees()]
    # Add "Select Name" option at the beginning of the list
    employee_choices.insert(0, ('', 'Select Name'))

    form.name_employee.choices = employee_choices
    form.name_employee1.choices = employee_choices
    form.name_employee2.choices = employee_choices

    # Set the default selected store, if available
    if selected_store:
        form.selected_store.data = selected_store.id

    return render_template('dailysales.html', form=form, user_stores=user_stores)


@terminal.route('/dailysales', methods=['GET', 'POST'])
@employee_required
def dailysales():
    user_stores, selected_store = fetch_user_stores(current_user)
    form = DailySalesSubmitForm()

    # Get the list of employees using the Swingbyemployees function
    employee_choices = [(user.id, user.name) for user in Swingbyemployees()]

    # Debug print to see if employee choices are being pulled
    print("Employee Choices:", employee_choices)

    # Set choices for employee input boxes
    form.name_employee.choices = employee_choices
    form.name_employee1.choices = employee_choices
    form.name_employee2.choices = employee_choices

    form.selected_store.choices = [(store.id, store.name) for store in user_stores]

    if selected_store:
        form.selected_store.data = selected_store.id

    if form.validate_on_submit():
        # Process form submission
        # ...

        return render_template('dailysales.html', form=form, user_stores=user_stores, selected_store=selected_store)

def fetch_recent_daily_sales(store_id):
    return (
        DailySales.query
        .filter_by(store_id=store_id)
        .order_by(desc(DailySales.date))
        .limit(31)
        .all()
    )

@terminal.route('/submit_dailysales', methods=['GET', 'POST'])
@employee_required
def dailysales_submit():
    user_stores, selected_store = fetch_user_stores(current_user)
    form = DailySalesSubmitForm()
    form.selected_store.choices = [(store.id, store.name) for store in user_stores]
    employee_choices = [(user.id, user.name) for user in Swingbyemployees()]
    
    # Set choices for employee input boxes
    employee_choices = [("", "Select Employee")] + [(user.id, user.name) for user in Swingbyemployees()]
    form.name_employee.choices = employee_choices
    form.name_employee1.choices = employee_choices
    form.name_employee2.choices = employee_choices
         # If there is a selected store, set it as the default
    if selected_store:
        form.selected_store.data = selected_store.id

    if form.validate_on_submit():
            employee1_id = form.name_employee1.data or None
            employee2_id = form.name_employee2.data or None

            try:
                overwrite = form.overwrite.data
                existing_entry = DailySales.query.filter_by(date=form.date.data).first()

                if existing_entry and not overwrite:
                    flash('An entry for this date already exists. Check the overwrite box if you want to overwrite it.', 'warning')
                else:
                    if existing_entry and overwrite:
                        # Update the existing entry with form data
                        existing_entry.store_id = form.selected_store.data
                        existing_entry.name_employee = form.name_employee.data
                        existing_entry.hours_employee = form.hours_employee.data
                        existing_entry.name_employee1 = form.name_employee1.data
                        existing_entry.hours_employee1 = form.hours_employee1.data
                        existing_entry.name_employee2 = form.name_employee2.data
                        existing_entry.hours_employee2 = form.hours_employee2.data
                        existing_entry.total_sales_shift1 = form.total_sales_shift1.data
                        existing_entry.total_sales_shift2 = form.total_sales_shift2.data
                        existing_entry.card_total_shift1 = form.card_total_shift1.data
                        existing_entry.card_total_shift2 = form.card_total_shift2.data
                        existing_entry.drop_total_shift1 = form.drop_total_shift1.data
                        existing_entry.drop_total_shift2 = form.drop_total_shift2.data
                        existing_entry.lotto_payout_shift1 = form.lotto_payout_shift1.data
                        existing_entry.lotto_payout_shift2 = form.lotto_payout_shift2.data
                        existing_entry.payout1_shift1 = form.payout1_shift1.data
                        existing_entry.payout1_shift2 = form.payout1_shift2.data
                        existing_entry.payout2_shift1 = form.payout2_shift1.data
                        existing_entry.payout2_shift2 = form.payout2_shift2.data
                        existing_entry.total_sales_day = form.total_sales_day.data
                        existing_entry.card_total_day = form.card_total_day.data
                        existing_entry.drop_total_day = form.drop_total_day.data
                        existing_entry.lotto_payout_day = form.lotto_payout_day.data
                        existing_entry.payout1_day = form.payout1_day.data
                        existing_entry.payout2_day = form.payout2_day.data
                        existing_entry.over_short = form.over_short.data
                        existing_entry.bonus_for_day=form.bonus_for_day.data

                        db.session.commit()
                        flash('Entry for this date was successfully overwritten.', 'success')
                    else:
                        # Create a new entry
                        daily_sales_entry = DailySales(
                            date=form.date.data,
                            store_id=form.selected_store.data,
                            name_employee=form.name_employee.data,
                            hours_employee=form.hours_employee.data,
                            name_employee1=form.name_employee1.data,
                            hours_employee1=form.hours_employee1.data,
                            name_employee2=form.name_employee2.data,
                            hours_employee2=form.hours_employee2.data,
                            total_sales_shift1=form.total_sales_shift1.data,
                            total_sales_shift2=form.total_sales_shift2.data,
                            card_total_shift1=form.card_total_shift1.data,
                            card_total_shift2=form.card_total_shift2.data,
                            drop_total_shift1=form.drop_total_shift1.data,
                            drop_total_shift2=form.drop_total_shift2.data,
                            lotto_payout_shift1=form.lotto_payout_shift1.data,
                            lotto_payout_shift2=form.lotto_payout_shift2.data,
                            payout1_shift1=form.payout1_shift1.data,
                            payout1_shift2=form.payout1_shift2.data,
                            payout2_shift1=form.payout2_shift1.data,
                            payout2_shift2=form.payout2_shift2.data,
                            total_sales_day=form.total_sales_day.data,
                            card_total_day=form.card_total_day.data,
                            drop_total_day=form.drop_total_day.data,
                            lotto_payout_day=form.lotto_payout_day.data,
                            payout1_day=form.payout1_day.data,
                            payout2_day=form.payout2_day.data,
                            bonus_for_day=form.bonus_for_day.data,
                            over_short=form.over_short.data
                        )
                        db.session.add(daily_sales_entry)
                        db.session.commit()
                        flash('New entry was successfully added.', 'success')

                return redirect(url_for('terminal.dailysales'))  # Redirect after successful form processing
            except Exception as e:
                flash('An error occurred: {}'.format(e), 'error')
                # Make sure to return a response even in case of exception
    if selected_store is None:
        daily_sales_data = []
    else:
        daily_sales_data = DailySales.query.filter_by(store_id=selected_store.id).all()
            # Render the form for GET request or if form is not valid
    recent_daily_sales_entries = []
    if selected_store:
        recent_daily_sales_entries = fetch_recent_daily_sales(selected_store.id)
    return render_template('dailysales.html', form=form, user_stores=user_stores,  selected_store=selected_store, recent_daily_sales_entries=recent_daily_sales_entries)

def fetch_recent_daily_sales(store_id):
    return (
        DailySales.query
        .filter_by(store_id=store_id)
        .order_by(desc(DailySales.date))
        .limit(31)
        .all()
    )
    return render_template('dailysales.html', form=form, user_stores=user_stores,  selected_store=selected_store)

#<----- Daily Sales End ----->#

#<----- Daily Store Transfer ----->#

@terminal.route('/store_transfer', methods=['GET', 'POST'])
@employee_required
def store_transfer():
    user_stores, selected_store = fetch_user_stores(current_user)
    form = StoreTransferForm()
    form.set_store_choices([(str(store.id), store.name) for store in user_stores])

    if form.validate_on_submit():
        transfer_number = form.transfer_number.data.strip()
        # Normalize the transfer number to ensure consistent formatting
        normalized_transfer_number = transfer_number.lstrip('0')

        # Fetch potential duplicates considering leading zeros
        potential_duplicates = db.session.query(StoreTransfer).all()
        duplicate_transfers = [dt for dt in potential_duplicates if dt.transfer_number.lstrip('0') == normalized_transfer_number]

        if form.transferred_from.data == form.transferred_to.data:
            flash("Transferred From and Transferred To cannot be the same store.", "danger")
        elif duplicate_transfers:
            overwrite = request.form.get('overwrite') == 'on'
            if overwrite:
                # Delete all duplicates
                for duplicate_transfer in duplicate_transfers:
                    db.session.delete(duplicate_transfer)
                db.session.commit()  # Commit deletion before adding a new record

                # Add the new transfer record
                add_new_transfer_record(form)
                flash("Store Transfer updated successfully, old records overwritten.", "success")
                return redirect(url_for('terminal.store_transfer'))
            else:
                flash("Duplicate Transfer Number found. Please check to overwrite if needed.", "warning")
        else:
            # No duplicate, add new transfer record
            add_new_transfer_record(form)
            return redirect(url_for('terminal.store_transfer'))
   
   # Assuming 'selected_store' contains the ID of the store selected by the user
    if selected_store is not None:
        selected_store_id = selected_store.id  # Adjust based on your actual data structure
        transfers = get_transfers_with_store_names(selected_store_id)
    else:
        transfers = []


    return render_template('store_transfer.html', form=form, transfers=transfers, selected_store=selected_store, user_stores=user_stores)


def get_transfers_with_store_names(selected_store_id):
    # Aliasing Store model for self-join
    StoreFrom = aliased(Store, name="store_from")
    StoreTo = aliased(Store, name="store_to")

    transfers = db.session.query(
        StoreTransfer.date,
        StoreTransfer.transfer_number,
        StoreFrom.name.label("transferred_from_name"),
        StoreTo.name.label("transferred_to_name"),
        StoreTransfer.amount,
        StoreTransfer.remark
    ).join(
        StoreFrom, StoreTransfer.transferred_from == StoreFrom.id
    ).join(
        StoreTo, StoreTransfer.transferred_to == StoreTo.id
    ).filter(
        or_(
            StoreTransfer.transferred_from == selected_store_id,
            StoreTransfer.transferred_to == selected_store_id
        )
    ).order_by(desc(StoreTransfer.date)).limit(100).all()

    return transfers


## Adding Transfer Record ##
def add_new_transfer_record(form):
    new_transfer = StoreTransfer(
        date=form.date.data,
        transfer_number=form.transfer_number.data.strip(),  # Ensure transfer_number is processed as a string
        transferred_from=int(form.transferred_from.data),  # Convert to int since form data is string
        transferred_to=int(form.transferred_to.data),  # Convert to int
        amount=form.amount.data,
        remark=form.remark.data
    )
    db.session.add(new_transfer)
    try:
        db.session.commit()
        flash("Store Transfer added successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("An error occurred while adding the store transfer.", "danger")

#<----- Daily Store Transfer End ----->#
#<----- Daily Expenses ----->#

@terminal.route('/expenses', methods=['GET', 'POST'])
@manager_required
def expenses():
    user_stores, selected_store = fetch_user_stores(current_user)

    form = ExpenseForm()
    form.expense_type.choices = [(etype, etype) for etype in expense_types]
    form.expense_pay_type.choices = [(ptype, ptype) for ptype in payment_types]

    if form.validate_on_submit():
        store_id = selected_store.id if selected_store else None

        new_expense = Expense(
            expense_date=form.expense_date.data,
            expense_type=form.expense_type.data,
            expense_description=form.expense_description.data,
            expense_amount=form.expense_amount.data,
            expense_pay_type=form.expense_pay_type.data,
            store_id=store_id
        )

        db.session.add(new_expense)
        db.session.commit()

        flash("Expense added successfully.", "success")
        return redirect(url_for('terminal.expenses'))

    if selected_store is None:
         expenses = []
    else:
        expenses = (
            db.session.query(Expense, Store.name) 
            .join(Store, Expense.store_id == Store.id)
            .filter(Store.id == selected_store.id)
            .order_by(desc(Expense.expense_date))
            .limit(100)
            .all()
        )

    return render_template('expenses.html', form=form, expenses=expenses, selected_store=selected_store, user_stores=user_stores)

#<----- Daily Expeses End ----->#

#<----- Daily Purchase ----->#

@terminal.route('/purchase_order', methods=['GET', 'POST'])
@owner_required
def purchase_order():
    authorized_stores = get_user_stores(current_user)
    default_store = session.get('selected_store') if current_user.is_authenticated else None

    form = PurchaseOrderForm()
    form.store_id.choices = [(store.id, store.name) for store in authorized_stores]
    form.payment_method.choices = [(ptype, ptype) for ptype in payment_types]

    if default_store:
        form.store_id.data = default_store  # Set the default value

    if form.validate_on_submit():
        # Debug: Print submitted form data
        print("Submitted form data:", form.data)

        try:
            new_purchase_order = PurchaseOrder(
                date=form.date.data,
                po_number=form.po_number.data,
                vendor_name=form.vendor_name.data,
                invoice_total=form.invoice_total.data,
                payment_method=form.payment_method.data,
                received_by=form.received_by.data,
                store_id=form.store_id.data
            )

            db.session.add(new_purchase_order)
            db.session.commit()
            flash("Purchase order added successfully.", "success")
        except Exception as e:
            db.session.rollback()
            print("Error when adding purchase order:", e)
            flash("Error when adding purchase order. " + str(e), "error")

        return redirect(url_for('terminal.purchase_order'))

    # Fetch purchase orders
    if default_store:
        purchase_orders = PurchaseOrder.query.filter_by(store_id=default_store).order_by(PurchaseOrder.date.desc()).limit(100).all()
    else:
        purchase_orders = []

    return render_template('purchase_order.html', form=form, purchase_orders=purchase_orders, stores=authorized_stores, default_store=default_store)





    today = datetime.utcnow()
    half_month_intervals = generate_half_month_intervals(today.year, today.month)
    all_user_daily_sales = []
    for start_date, end_date in half_month_intervals:
        daily_sales_query = DailySales.query.filter(
            ((DailySales.name_employee == user_name) |
             (DailySales.name_employee1 == user_name) |
             (DailySales.name_employee2 == user_name)) &
            (DailySales.date >= start_date) &
            (DailySales.date <= end_date)
        ).all()
        all_user_daily_sales.append((start_date, end_date, daily_sales_query))
    return all_user_daily_sales

#<----- Daily Purchase End ----->#

#<-----  Employee Central   ----->#

# Extracting the hours worked

def get_current_pay_period():
    today = datetime.today()
    year = today.year
    month = today.month
    middle_of_month = 16

    if today.day < middle_of_month:
        # We are in the first pay period of the month
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 15)
    else:
        # We are in the second pay period of the month
        start_date = datetime(year, month, 16)
        # End date is the last day of the month
        if month == 12:  # December
            end_date = datetime(year, month, 31)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    return start_date, end_date


def get_user_daily_sales_for_period(user_name, start_date, end_date):
    user_daily_sales = DailySales.query.filter(
        and_(
            ((DailySales.name_employee == user_name) |
             (DailySales.name_employee1 == user_name) |
             (DailySales.name_employee2 == user_name)),
            (DailySales.date >= start_date),
            (DailySales.date <= end_date)
        )
    ).all()
    return user_daily_sales

@terminal.route('/employee')
def employee():
    if current_user.is_authenticated:
        # Get start and end dates for the current pay period
        start_date, end_date = get_current_pay_period()

        # Check if parameters for start and end dates are provided in the URL
        start_date_param = request.args.get('start_date')
        end_date_param = request.args.get('end_date')

        if start_date_param and end_date_param:
            # Parse start and end dates from URL parameters
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d')

        # Calculate start and end dates for the previous pay period
        previous_end_date = start_date - timedelta(days=1)
        previous_start_date = previous_end_date.replace(day=1)

        # Get user's daily sales data for the specified pay period
        user_name = current_user.name
        user_daily_sales = get_user_daily_sales_for_period(user_name, start_date, end_date)

        # Get user's daily sales data for the previous pay period
        previous_user_daily_sales = get_user_daily_sales_for_period(user_name, previous_start_date, previous_end_date)

        # Pass data to the template
        return render_template('employee.html', user_daily_sales=user_daily_sales,
                               start_date=start_date, end_date=end_date,
                               previous_user_daily_sales=previous_user_daily_sales,
                               previous_start_date=previous_start_date, previous_end_date=previous_end_date)
    else:
        return render_template('login.html')


@terminal.route('/employeeintake', methods=['GET', 'POST'])
def employee_intake():
    form = EmployeeIntakeForm()
    form_files = os.listdir('static/employeeforms')  # List PDFs in the folder

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            # Save the file logic here

            # Update session with the upload status
            session['uploaded_files'] = session.get('uploaded_files', [])
            session['uploaded_files'].append(filename)

        if form.validate_on_submit():
            # Process form data here, e.g., save data to a database
            flash('Employee intake form submitted successfully!', 'success')
            return redirect(url_for('employee_intake'))  # Redirect as needed

    uploaded_files = session.get('uploaded_files', [])
    return render_template('employeeintake.html', form=form, form_files=form_files, uploaded_files=uploaded_files)


@terminal.route('/form-upload')
def form_upload():
    form_files = os.listdir('static/employeeforms')
    return render_template('form_upload.html', form_files=form_files)


#<----- Employee Central End ----->#


@terminal.route('/monthly_paperwork')
@manager_required
def monthly_paperwork():
    return render_template('monthly_paperwork.html')


@terminal.route('/misc')
def misc():
    return "Hello World"

#<----- Monthly Employee   ----->#

def handle_schedule_submission(form):
    if request.method == 'POST' and form.validate_on_submit():
        # Assuming 'Schedule' is your model and 'db' is your SQLAlchemy instance
        for daily_schedule in form.daily_schedules.data:
            new_schedule = Schedule(
                store_id=form.store_id.data,
                date=daily_schedule['date'],
                day=daily_schedule['day'],
                employee1=daily_schedule['employee1'],
                start1=daily_schedule['start1'],
                finish1=daily_schedule['finish1'],
                employee2=daily_schedule.get('employee2', ''),
                start2=daily_schedule.get('start2', None),
                finish2=daily_schedule.get('finish2', None),
                employee3=daily_schedule.get('employee3', ''),
                start3=daily_schedule.get('start3', None),
                finish3=daily_schedule.get('finish3', None)
            )
            db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return True  # Indicate successful processing
    return False  # Indicate that the form was not submitted or not valid

def handle_schedule_retrieval(retrieval_form):
    """
    Handle the retrieval of schedules based on the provided form data.
    """
    # Fetching employee and manager users
    employee_and_manager_users = Swingbyemployees()
    
    # Extracting employee choices
    employee_choices = [(0, "Select Employee")] + [(user.id, user.name) for user in employee_and_manager_users]
    
    # Filtering schedules based on form data
    schedules = Schedule.query.filter(
        Schedule.store_id == retrieval_form.store_id.data,
        Schedule.date >= retrieval_form.start_date.data,
        Schedule.date <= retrieval_form.end_date.data
    ).all()
    
    return schedules, employee_choices

def retrieve_hours_worked(selected_store):
    # Fetch daily sales records for the selected store
    daily_sales_records = DailySales.query.filter_by(store_id=selected_store).all() if selected_store else DailySales.query.all()
    
    # Extract relevant data from the records
    extracted_data = [{'date': record.date, 'name_employee': record.name_employee, 'hours_employee': record.hours_employee, 'store_id': record.store_id} for record in daily_sales_records]
    
    return extracted_data

@terminal.route('/temployee', methods=['GET', 'POST'])
def temployee():
    # Initialize schedule and retrieval forms
    schedule_form = ScheduleForm()
    retrieval_form = ScheduleRetrievalForm()
    
    # Fetch store choices
    stores = Store.query.all()
    store_choices = [(store.id, store.name) for store in stores]
    schedule_form.store_id.choices = store_choices
    retrieval_form.store_id.choices = store_choices

    # Fetch employee choices and populate them in daily schedule forms
    employee_and_manager_users = Swingbyemployees()
    employee_choices = [(0, "Select Employee")] + [(user.id, user.name) for user in employee_and_manager_users]
    for daily_schedule_form in schedule_form.daily_schedules:
        daily_schedule_form.employee1.choices = employee_choices
        daily_schedule_form.employee2.choices = employee_choices
        daily_schedule_form.employee3.choices = employee_choices

    # Fetch selected store
    selected_store = request.args.get('store')

    # Retrieve hours worked data
    extracted_data = retrieve_hours_worked(selected_store)

    # Initialize schedules variable for template
    schedules = None

    # Determine which form was submitted
    if 'submit_schedule' in request.form and schedule_form.validate():
        # Handle schedule submission
        handle_schedule_submission(schedule_form)
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('terminal.temployee'))
    elif 'retrieve_schedule' in request.form and retrieval_form.validate():
        # Handle schedule retrieval
        schedules, employee_choices = handle_schedule_retrieval(retrieval_form)
        flash('Schedules retrieved successfully!', 'info')  # Optional: provide feedback

    # Render template with all context variables, including employee_choices
    return render_template(
        'temployee.html', 
        schedule_form=schedule_form, 
        retrieval_form=retrieval_form, 
        schedules=schedules, 
        data=extracted_data, 
        stores=stores, 
        selected_store=selected_store,
        employee_and_manager_users=employee_and_manager_users,  # Passing employee_and_manager_users to the template
        employee_choices=employee_choices  # Passing employee_choices to the template
    )

#<----- Monthly Employee  End ----->#



#<----- Monthly P/L   ----->#

def get_monthly_total_sales(selected_month, selected_year, selected_store_id):
    # Start of the month
    start_date = datetime(selected_year, selected_month, 1)
    
    # End of the month calculation can be tricky due to varying days in months
    # A neat trick is to start at the first of the next month and subtract a day
    # But we need to handle December (month 12) specially to roll over to the next year
    if selected_month == 12:
        end_date = datetime(selected_year + 1, 1, 1)
    else:
        end_date = datetime(selected_year, selected_month + 1, 1)
    
    # Query to sum total_sales_day for the selected month, year, and store
    total_sales = db.session.query(func.sum(DailySales.total_sales_day)).filter(
        DailySales.store_id == selected_store_id,
        DailySales.date >= start_date,
        DailySales.date < end_date  # Notice the end_date is not included
    ).scalar()
    
    return total_sales or 0.0  # Return 0.0 if the result is None

def get_total_net_transfers(net_transfers):
    # Initialize two variables to track incoming (amounts owed to your store) and outgoing (amounts your store owes)
    incoming_balance = Decimal('0.0')
    outgoing_balance = Decimal('0.0')
    
    # Iterate through each transfer to determine if it's incoming or outgoing
    for transfer in net_transfers:
        if "owes Swingby Maypearl" in transfer['comment']:
            # This is an amount owed to your store, so add it to the incoming_balance
            incoming_balance += Decimal(transfer['net_balance'])
        else:
            # This is an amount your store owes, so add it to the outgoing_balance
            outgoing_balance += Decimal(transfer['net_balance'])
    
    # The overall balance is the difference between incoming and outgoing balances
    overall_balance = incoming_balance - outgoing_balance
    return overall_balance

def get_total_monthly_purchase_payable(selected_month, selected_year, selected_store_id):
    # Get the total amount of purchases
    total_purchases = get_total_monthly_purchases(selected_month, selected_year, selected_store_id)
    
    # Get the purchases by payment type
    purchases_by_payment_type = get_purchases_by_payment_type(selected_month, selected_year, selected_store_id)
    
    # Extract the "Payable" amount from the purchases by payment type
    payable_amount = purchases_by_payment_type.get("Payable", Decimal('0.0'))
    
    # Subtract the "Payable" amount from the total purchases to get the total monthly purchase payable
    total_monthly_purchase_payable = total_purchases - payable_amount

    return total_monthly_purchase_payable

@terminal.route('/profit_loss', methods=['GET', 'POST'])
@login_required
def profit_loss():
    form = MonthlyPaperworkForm()
    user_stores = get_user_stores(current_user)
    form.selected_store.choices = [(store.id, store.name) for store in user_stores]

    # Initialize all variables with default values
    total_expenses = Decimal('0.0')
    expenses_by_type = {}
    total_purchases = Decimal('0.0')
    purchases_by_payment_type = {}
    total_monthly_purchase_payable = Decimal('0.0')
    net_transfers = []
    overall_balance = Decimal('0.0')
    monthly_total_sales = Decimal('0.0')
    net_profit_loss = Decimal('0.0')  # Initialize net_profit_loss here

    if form.validate_on_submit():
        selected_month = form.selected_month.data
        selected_year = form.selected_year.data
        selected_store_id = form.selected_store.data

        # Fetch and calculate financial data
        total_expenses = get_total_monthly_expenses(selected_month, selected_year, selected_store_id)
        expenses_by_type = get_total_expenses_by_type(selected_month, selected_year, selected_store_id)
        total_purchases = get_total_monthly_purchases(selected_month, selected_year, selected_store_id)
        purchases_by_payment_type = get_purchases_by_payment_type(selected_month, selected_year, selected_store_id)
        total_monthly_purchase_payable = get_total_monthly_purchase_payable(selected_month, selected_year, selected_store_id)
        monthly_total_sales = Decimal(get_monthly_total_sales(selected_month, selected_year, selected_store_id) or 0.0)
        
        # Calculate net transfers and overall balance
        net_transfers = calculate_net_transfers(selected_month, selected_year, selected_store_id)
        overall_balance = get_total_net_transfers(net_transfers)

        # Adjusted calculation for net profit/loss
        # Assuming you want to calculate net profit/loss as sales minus expenses
        net_profit_loss = monthly_total_sales + overall_balance - total_expenses - total_monthly_purchase_payable # Adjust according to your financial model

    return render_template('profit_loss.html', form=form,
                           monthly_total_sales=monthly_total_sales,
                           total_expenses=total_expenses,
                           net_profit_loss=net_profit_loss,
                           expenses_by_type=expenses_by_type,
                           total_purchases=total_purchases,
                           purchases_by_payment_type=purchases_by_payment_type,
                           total_monthly_purchase_payable=total_monthly_purchase_payable,
                           net_transfers=net_transfers,
                           overall_balance=overall_balance,
                           selected_month=selected_month if form.validate_on_submit() else None,
                           selected_year=selected_year if form.validate_on_submit() else None,
                           selected_store_id=selected_store_id if form.validate_on_submit() else None)

#<----- Monthly P/L  End ----->#



#<----- Monthly Purchase Order ----->#

def get_total_monthly_purchases(selected_month, selected_year, selected_store_id):
    # Calculate total purchases for the selected month, year, and store
    total_purchases = db.session.query(func.sum(PurchaseOrder.invoice_total)).filter(
        func.extract('year', PurchaseOrder.date) == selected_year,
        func.extract('month', PurchaseOrder.date) == selected_month,
        PurchaseOrder.store_id == selected_store_id  # Filter by selected store
    ).scalar() or Decimal('0.0')

    return total_purchases

def get_purchases_by_payment_type(selected_month, selected_year, selected_store_id):
    # Initialize the dictionary with all payment types set to zero
    purchases_by_payment_type = {pt: Decimal('0.0') for pt in payment_types}

    # Perform database query and calculations
    for payment_type in payment_types:
        total_purchase_by_payment = db.session.query(func.sum(PurchaseOrder.invoice_total)).filter(
            PurchaseOrder.payment_method == payment_type,
            func.extract('year', PurchaseOrder.date) == selected_year,
            func.extract('month', PurchaseOrder.date) == selected_month,
            PurchaseOrder.store_id == selected_store_id  # Filter by selected store
        ).scalar() or Decimal('0.0')
        
        purchases_by_payment_type[payment_type] = total_purchase_by_payment

    return purchases_by_payment_type

def get_purchases_by_vendor(selected_month, selected_year, selected_store_id):
    # Retrieve vendors and their total purchases, and total purchases by payment method
    vendors_and_purchases = db.session.query(
        PurchaseOrder.vendor_name,
        PurchaseOrder.payment_method,
        func.sum(PurchaseOrder.invoice_total)
    ).filter(
        func.extract('year', PurchaseOrder.date) == selected_year,
        func.extract('month', PurchaseOrder.date) == selected_month,
        PurchaseOrder.store_id == selected_store_id  # Filter by selected store
    ).group_by(PurchaseOrder.vendor_name, PurchaseOrder.payment_method).all()

    # Initialize vendor purchases with all payment types set to zero
    vendor_purchases = {}
    for vendor, payment_method, total in vendors_and_purchases:
        if vendor not in vendor_purchases:
            # Initialize with zero totals for each payment type
            vendor_purchases[vendor] = {'total_purchase': Decimal('0.0')}
            for pt in payment_types:
                vendor_purchases[vendor][pt] = Decimal('0.0')
        
        # Add totals to the respective payment method and to the total purchase
        if payment_method in payment_types:  # Ensure the payment method is in your list
            vendor_purchases[vendor][payment_method] += total
        vendor_purchases[vendor]['total_purchase'] += total

    # Convert to list of dictionaries for easier template processing
    vendor_purchases_list = [
        {
            'vendor_name': vendor,
            'total_purchase': f"${totals['total_purchase']:.2f}",
            **{pt: f'${totals[pt]:.2f}' for pt in payment_types}  # Include each payment type's total
        } for vendor, totals in vendor_purchases.items()
    ]

    return vendor_purchases_list

@terminal.route('/tpurchase_order', methods=['GET', 'POST'])
def tpurchase_order():
    form = TotalPurchaseOrderForm()

    # Populate the store choices (you can get the list of stores from your database)
    form.selected_store.choices = [(store.id, store.name) for store in Store.query.all()]

    if form.validate_on_submit():
        selected_month = form.selected_month.data
        selected_year = form.selected_year.data
        selected_store_id = form.selected_store.data

        # Calculate total monthly purchases (pass selected_store_id)
        total_monthly_purchases = get_total_monthly_purchases(selected_month, selected_year, selected_store_id)

        # Calculate total purchases by payment type (pass selected_store_id)
        purchases_by_payment_type = get_purchases_by_payment_type(selected_month, selected_year, selected_store_id)

        # Calculate total purchases by vendor (pass selected_store_id)
        vendor_purchases = get_purchases_by_vendor(selected_month, selected_year, selected_store_id)

        # Get purchase order data
        purchase_orders = get_purchase_order_data(selected_month, selected_year, selected_store_id)
       
        data = {
            'total_monthly_purchases': f'${total_monthly_purchases}',
            'purchases_by_payment_type': purchases_by_payment_type,
            'vendor_purchases': vendor_purchases,
            'payment_types': payment_types,  # pass payment_types to your template                        
            'purchase_orders': purchase_orders,  # Pass purchase order data to the template
            'selected_store_id': selected_store_id  # pass selected_store_id to your template
        }

        return render_template('tpurchase_order.html', form=form, **data)

    # Initial load or no POST request
# Initial load or no POST request
    return render_template('tpurchase_order.html', form=form,
                           total_monthly_purchases='$0.00',
                           purchases_by_payment_type={},
                           vendor_purchases=[],
                           purchase_orders=[])  # Ensure purchase_orders is passed as empty list initially

def get_purchase_order_data(selected_month, selected_year, selected_store_id):
    # Convert selected_month and selected_year to integers
    selected_month = int(selected_month)
    selected_year = int(selected_year)

    start_date = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = datetime(selected_year + 1, 1, 1)
    else:
        end_date = datetime(selected_year, selected_month + 1, 1)

    purchase_orders = PurchaseOrder.query.filter(
        PurchaseOrder.date >= start_date,
        PurchaseOrder.date < end_date,
        PurchaseOrder.store_id == selected_store_id
    ).all()

    return purchase_orders


# PO Edit Bulk #

@terminal.route('/po_edit')
def po_edit():  
    return render_template('po_edit.html')

#<----- Monthly Purchase Order End ----->#


#<----- Monthly Expenses Section ----->#
def get_total_monthly_expenses(selected_month, selected_year, selected_store_id):
    # Calculate total expenses for the selected month, year, and store
    total_expenses = db.session.query(func.sum(Expense.expense_amount)).filter(
        func.extract('year', Expense.expense_date) == selected_year,
        func.extract('month', Expense.expense_date) == selected_month,
        Expense.store_id == selected_store_id  # Filter by selected store
    ).scalar() or Decimal('0.0')

    return total_expenses

def get_total_expenses_by_type(selected_month, selected_year, selected_store_id):
    # Calculate total expenses by expense type for the selected month, year, and store
    expenses_by_type = {}

    for expense_type in expense_types:
        total_expense_by_type = db.session.query(func.sum(Expense.expense_amount)).filter(
            func.extract('year', Expense.expense_date) == selected_year,
            func.extract('month', Expense.expense_date) == selected_month,
            Expense.expense_type == expense_type,
            Expense.store_id == selected_store_id  # Filter by selected store
        ).scalar() or Decimal('0.0')
        
        expenses_by_type[expense_type] = total_expense_by_type

    return expenses_by_type

def get_expenses_by_payment_type(selected_month, selected_year, selected_store_id):
    # Calculate total expenses by payment type for the selected month, year, and store
    expenses_by_payment_type = {}

    for payment_type in payment_types:
        total_expense_by_payment_type = db.session.query(func.sum(Expense.expense_amount)).filter(
            func.extract('year', Expense.expense_date) == selected_year,
            func.extract('month', Expense.expense_date) == selected_month,
            Expense.expense_pay_type == payment_type,
            Expense.store_id == selected_store_id  # Filter by selected store
        ).scalar() or Decimal('0.0')
        
        expenses_by_payment_type[payment_type] = total_expense_by_payment_type

    return expenses_by_payment_type


@terminal.route('/texpenses', methods=['GET', 'POST'])
def texpenses():
    form = TExpensesForm()

    # Populate form choices (example: for months and years)
    form.selected_month.choices = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.now().year
    form.selected_year.choices = [(str(year), str(year)) for year in range(current_year - 6, current_year + 1)]
    form.selected_store.choices = [(str(store.id), store.name) for store in Store.query.all()]

    if form.validate_on_submit():
        selected_month = form.selected_month.data
        selected_year = form.selected_year.data
        selected_store_id = form.selected_store.data

        total_monthly_expenses = get_total_monthly_expenses(selected_month, selected_year, selected_store_id)
        expenses_by_type = get_total_expenses_by_type(selected_month, selected_year, selected_store_id)
        expenses_by_payment_type = get_expenses_by_payment_type(selected_month, selected_year, selected_store_id)
    else:
        total_monthly_expenses = 0
        expenses_by_type = {}
        expenses_by_payment_type = {}

    return render_template('texpenses.html', form=form, 
                           total_monthly_expenses=total_monthly_expenses,
                           expenses_by_type=expenses_by_type,
                           expenses_by_payment_type=expenses_by_payment_type)

#<----- End Monthly Expenses ----->#


#<----- Monthly Transfer ----->#

@terminal.route('/tstore_transfer', methods=['GET', 'POST'])
@login_required  # Or @employee_required if you have a custom decorator
def tstore_transfer():
    form = TStoreTransferForm()

    # Setup form choices with a "Select Store" default
    form.selected_month.choices = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.now().year
    form.selected_year.choices = [(str(year), str(year)) for year in range(current_year - 10, current_year + 1)]
    form.selected_store.choices = [("0", "Select Store")] + [(str(store.id), store.name) for store in Store.query.all()]

    print("Form loaded with choices.")

    if form.validate_on_submit():
        print("Form validated.")
        selected_month = int(form.selected_month.data)
        selected_year = int(form.selected_year.data)
        selected_store_id = int(form.selected_store.data)

        print(f"Selected month: {selected_month}, year: {selected_year}, store ID: {selected_store_id}")

        if selected_store_id == 0:
            flash('Please select a store.', 'warning')
            print("No store selected.")
            return redirect(url_for('terminal.tstore_transfer'))

        transfer_totals_by_store = get_transfer_totals_by_store(selected_month, selected_year, selected_store_id)

        transfer_totals = calculate_store_transfer_totals(selected_month, selected_year, selected_store_id)

        net_transfers = calculate_net_transfers(selected_month, selected_year, selected_store_id)


        transfers = get_monthly_store_transfers(selected_month, selected_year, selected_store_id)

        # Pass the aggregated totals to the template
        return render_template('tstore_transfer.html', form=form, transfers=transfers, net_transfers=net_transfers, transfer_totals=transfer_totals, transfer_totals_by_store=transfer_totals_by_store)
    
    print("Form not validated or GET request.")
    return render_template('tstore_transfer.html', form=form, transfers=[], transfer_totals_by_store=[], net_transfers=[])

## Calculate total net transfers ##
def calculate_net_transfers(selected_month, selected_year, selected_store_id):
    selected_store_name = Store.query.get(selected_store_id).name
    net_balances = defaultdict(float)

    # Fetch incoming and outgoing transfers
    incoming_transfers = db.session.query(
        StoreTransfer.transferred_from,
        func.sum(StoreTransfer.amount).label('total_amount')
    ).filter(
        StoreTransfer.transferred_to == selected_store_id,
        db.extract('month', StoreTransfer.date) == selected_month,
        db.extract('year', StoreTransfer.date) == selected_year
    ).group_by(StoreTransfer.transferred_from).all()

    for transfer in incoming_transfers:
        partner_store_id = transfer[0]
        amount = transfer[1]
        net_balances[partner_store_id] -= amount  # Incoming means the selected store owes money

    outgoing_transfers = db.session.query(
        StoreTransfer.transferred_to,
        func.sum(StoreTransfer.amount).label('total_amount')
    ).filter(
        StoreTransfer.transferred_from == selected_store_id,
        db.extract('month', StoreTransfer.date) == selected_month,
        db.extract('year', StoreTransfer.date) == selected_year
    ).group_by(StoreTransfer.transferred_to).all()

    for transfer in outgoing_transfers:
        partner_store_id = transfer[0]
        amount = transfer[1]
        net_balances[partner_store_id] += amount  # Outgoing means the partner store owes money

    # Prepare final list with correct "owes" relationship
    net_transfers_named = []
    for store_id, balance in net_balances.items():
        partner_store_name = Store.query.get(store_id).name
        if balance > 0:
            comment = f"{partner_store_name} owes {selected_store_name} ${abs(balance)}"
        else:
            comment = f"{selected_store_name} owes {partner_store_name} ${abs(balance)}"

        net_transfers_named.append({
            'selected_store': selected_store_name,
            'partner_store': partner_store_name,
            'net_balance': abs(balance),
            'comment': comment
        })

    return net_transfers_named

## Total Transfers by Store Combination ##

def calculate_store_transfer_totals(selected_month, selected_year, selected_store_id):
    # Alias for stores to differentiate between "transferred_from" and "transferred_to"
    StoreFrom = aliased(Store, name='store_from')
    StoreTo = aliased(Store, name='store_to')
    
    totals = db.session.query(
        StoreFrom.name.label('transferred_from_name'),
        StoreTo.name.label('transferred_to_name'),
        func.sum(StoreTransfer.amount).label('total_amount')
    ).join(StoreFrom, StoreFrom.id == StoreTransfer.transferred_from) \
     .join(StoreTo, StoreTo.id == StoreTransfer.transferred_to) \
     .filter(
        db.or_(
            StoreTransfer.transferred_from == selected_store_id,
            StoreTransfer.transferred_to == selected_store_id
        ),
        db.extract('month', StoreTransfer.date) == selected_month,
        db.extract('year', StoreTransfer.date) == selected_year
    ).group_by(
        StoreFrom.name,
        StoreTo.name
    ).all()

    return totals



## All Transfers for month  In and Out ##
def get_transfer_totals_by_store(selected_month, selected_year, selected_store_id):
    # Aggregate incoming transfers
    incoming_totals = db.session.query(
        StoreTransfer.transferred_from, 
        db.func.sum(StoreTransfer.amount)
    ).filter(
        StoreTransfer.transferred_to == selected_store_id,
        db.extract('month', StoreTransfer.date) == selected_month,
        db.extract('year', StoreTransfer.date) == selected_year
    ).group_by(StoreTransfer.transferred_from).all()

    # Aggregate outgoing transfers
    outgoing_totals = db.session.query(
        StoreTransfer.transferred_to, 
        db.func.sum(StoreTransfer.amount)
    ).filter(
        StoreTransfer.transferred_from == selected_store_id,
        db.extract('month', StoreTransfer.date) == selected_month,
        db.extract('year', StoreTransfer.date) == selected_year
    ).group_by(StoreTransfer.transferred_to).all()

    # Combine and return results
    return incoming_totals + outgoing_totals

def get_monthly_store_transfers(selected_month, selected_year, selected_store_id):
    """
    Fetches all transfer records for a specific store within a given month and year.
    """
    transfers = StoreTransfer.query.filter(
        or_(
            StoreTransfer.transferred_from == selected_store_id,
            StoreTransfer.transferred_to == selected_store_id
        ),
        extract('month', StoreTransfer.date) == selected_month,
        extract('year', StoreTransfer.date) == selected_year
    ).order_by(StoreTransfer.date).all()

    return transfers

## <----- Till Here Transfer ------> ##




## <----- Show Daily Sales For Month ------> ##

@terminal.route('/tdaily_sales', methods=['GET', 'POST'])
def tdaily_sales():
    form = DailySalesForm()

    # Populate month and year choices
    form.selected_month.choices = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    current_year = datetime.now().year
    form.selected_year.choices = [(str(year), str(year)) for year in range(current_year - 10, current_year + 1)]

    # Populate store choices from the database
    form.selected_store.choices = [(str(store.id), store.name) for store in Store.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        selected_month = int(form.selected_month.data)
        selected_year = int(form.selected_year.data)
        selected_store_id = int(form.selected_store.data)

        daily_sales_data = DailySales.query.filter(
            db.func.extract('year', DailySales.date) == selected_year,
            db.func.extract('month', DailySales.date) == selected_month,
            DailySales.store_id == selected_store_id
        ).order_by(DailySales.date).all()

        # Calculate the total sales for the day
        total_sales_day = sum(daily.total_sales_day for daily in daily_sales_data if daily.total_sales_day is not None)

        return render_template(
            'tdaily_sales.html',
            form=form,
            daily_sales_data=daily_sales_data,
            total_sales_day=total_sales_day
        )

    # Initial page load or GET request
    return render_template('tdaily_sales.html', form=form, daily_sales_data=[], total_sales_day=0)


## <----- Till Here Month Sales daily ------> ##





#<----- Daily And Monthly Lottery ----->#

def process_lottery_entries(form, selected_store):
    store_id = form.selected_store.data
    expense_date = form.expense_date.data
    existing_entries = check_for_duplicates(store_id, expense_date, form.overwrite.data)
    if existing_entries is False:
        return False  # Stop processing if duplicates exist and overwrite is not enabled

    save_entries(form.entries.data, expense_date, store_id)
    db.session.commit()
    return True

def check_for_duplicates(store_id, expense_date, overwrite):
    existing_entries = LotteryEntry.query.filter_by(store_id=store_id, expense_date=expense_date).all()
    if existing_entries and not overwrite:
        flash('Duplicate entries for the selected date. Please select a different date or enable overwrite.', 'error')
        return False
    elif overwrite:
        for entry in existing_entries:
            db.session.delete(entry)
    return True

def save_entries(entries_data, expense_date, store_id):
    for index, entry_data in enumerate(entries_data, start=1):
        new_entry = LotteryEntry(
            row_number_entry=index,
            amount=entry_data['amount'],
            begin_day=entry_data['begin_day'],
            end_day=entry_data['end_day'],
            sold=entry_data['sold'],
            total=entry_data['total'],
            expense_date=expense_date,  # Ensure this is the correct field name in your model
            store_id=store_id,  # Ensure this is the correct field name in your model
        )
        db.session.add(new_entry)
    db.session.commit()  # Commit outside the loop

def process_day_lottery_entry(form, store_id, expense_date):
    # Check for existing entries (note the removal of .first())
    existing_entries = DayLotteryEntry.query.filter_by(store_id=store_id, date=expense_date).all()
    
    # If existing entries are found and overwrite is enabled, delete all existing entries
    if existing_entries and form.overwrite.data:
        for entry in existing_entries:
            db.session.delete(entry)
        db.session.commit()  # Commit the deletions here to ensure all are removed before adding a new one
        flash('All existing entries for the date were deleted. Overwriting with new data.', 'success')
    elif existing_entries:
        # If overwrite is not enabled and existing entries are found, halt processing and inform the user
        flash('Duplicate entries exist for this date. Enable overwrite to update.', 'warning')
        return False

    # Proceed to create a new entry after ensuring no duplicates exist
    new_entry = DayLotteryEntry(
        date=expense_date,
        store_id=store_id,
        total_scratch_off=form.total_scratch_off.data,
        total_online=form.total_online.data,
        actual_total=form.actual_total.data,
        pos_sale=form.pos_sale.data,
        over_short=form.over_short.data
    )
    db.session.add(new_entry)
    db.session.commit()
    return True

@login_required
@terminal.route('/lottery_input', methods=['GET', 'POST'])
def lottery_input():
    user_stores, selected_store = fetch_user_stores(current_user)
    store_choices = [(store.id, store.name) for store in user_stores]

    form = LotteryForm()
    day_lottery_form = DayLotteryEntryForm()

    form.selected_store.choices = store_choices
    day_lottery_form.selected_store.choices = store_choices

    if selected_store:
        form.selected_store.data = selected_store.id
        day_lottery_form.selected_store.data = selected_store.id

    if request.method == 'POST':
        action = request.form.get('action', 'submit')
        selected_store_id = request.form.get('selected_store')
        expense_date = request.form.get('expense_date', datetime.today().strftime('%Y-%m-%d'))
        expense_date_obj = datetime.strptime(expense_date, '%Y-%m-%d').date()

        form.selected_store.choices = store_choices
        form.expense_date.data = expense_date_obj
        day_lottery_form.selected_store.choices = store_choices
        day_lottery_form.expense_date.data = expense_date_obj

        if action == 'retrieve':
            recent_entries = get_most_recent_entries_before_date(selected_store_id, expense_date_obj)
            begin_day_values = {entry.row_number_entry: entry.end_day for entry in recent_entries}
            target_date_entries = LotteryEntry.query.filter_by(store_id=selected_store_id, expense_date=expense_date_obj).all()

            for i, entry_form in enumerate(form.entries):
                if i < len(target_date_entries):
                    entry = target_date_entries[i]
                    entry_form.populate_from_entry(entry)
                if i in begin_day_values:
                    entry_form.begin_day.data = begin_day_values[i]

            flash('Form pre-populated with last entry data.', 'success')

        elif action == 'submit':
            if form.validate() and day_lottery_form.validate():
                lottery_success = process_lottery_entries(form, selected_store_id)
                day_lottery_success = process_day_lottery_entry(day_lottery_form, selected_store_id, expense_date_obj)

                if lottery_success and day_lottery_success:
                    flash('All entries successfully submitted.', 'success')
                    return redirect(url_for('terminal.lottery_input'))
                else:
                    flash('An error occurred while submitting the forms. Please try again.', 'error')
            else:
                for fieldName, errorMessages in {**form.errors, **day_lottery_form.errors}.items():
                    for err in errorMessages:
                        flash(f"Error - {fieldName}: {err}", 'error')
       # Directly fetch 31 most recent day lottery entries for the selected store
    recent_day_lottery_entries = []
    if selected_store:
        recent_day_lottery_entries = (
            DayLotteryEntry.query
            .filter_by(store_id=selected_store.id)
            .order_by(desc(DayLotteryEntry.date))
            .limit(31)
            .all()
        )

    return render_template('lottery_input.html', 
                           form=form, 
                           day_lottery_form=day_lottery_form, 
                           selected_store=selected_store, 
                           user_stores=user_stores,
                           entries=recent_day_lottery_entries)


def get_most_recent_entries_before_date(store_id, target_date):
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    # Fetch most recent entries before target_date
    most_recent_date = db.session.query(db.func.max(LotteryEntry.expense_date)) \
        .filter(LotteryEntry.store_id == store_id, LotteryEntry.expense_date < target_date).scalar()

    if most_recent_date:
        return LotteryEntry.query.filter_by(store_id=store_id, expense_date=most_recent_date) \
            .order_by(LotteryEntry.row_number_entry.asc()).all()
    else:
        return []

@terminal.route('/fetch-data')
@login_required
def fetch_data():
    store_id = request.args.get('store_id')
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Check if entries exist for the target date
    existing_entries = LotteryEntry.query.filter_by(store_id=store_id, expense_date=target_date).all()

    if existing_entries:
        # If entries exist for the target date, return them directly
        data = {
            'entries': [
                {
                    'row_number_entry': entry.row_number_entry,
                    'amount': entry.amount,
                    'begin_day': entry.begin_day,
                    'end_day': entry.end_day,
                    'sold': entry.sold,
                    'total': entry.total,
                } for entry in existing_entries
            ]
        }
    else:
        # If no entries exist for the target date, fetch yesterday's data for pre-population
        yesterday = target_date - timedelta(days=1)
        yesterday_entries = LotteryEntry.query.filter_by(store_id=store_id, expense_date=yesterday).all()

        data = {
            'entries': [
                {
                    'row_number_entry': entry.row_number_entry,
                    'amount': entry.amount,  # Pre-populate with yesterday's amount
                    'begin_day': entry.end_day,  # Pre-populate yesterday's end day as today's begin day
                    'end_day': 0,  # Set to 0 or another logical default
                    'sold': 0,  # Set to 0 or another logical default
                    'total': 0,  # Set to 0 or another logical default
                } for entry in yesterday_entries
            ]
        }

    return jsonify(data)

@terminal.route('/fetch_day_lottery_data')
def fetch_day_lottery_data():
    store_id = request.args.get('store_id', type=int)
    date_str = request.args.get('date', default=datetime.today().strftime('%Y-%m-%d'), type=str)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        current_app.logger.error(f"Invalid date format: {date_str}")
        return jsonify({"error": "Invalid date format"}), 400

    current_app.logger.debug(f"Fetching day lottery data for Store ID: {store_id}, Date: {date_str}")
    entry = DayLotteryEntry.query.filter_by(store_id=store_id, date=date).first()

    if entry:
        data = {
            'total_scratch_off': str(entry.total_scratch_off),
            'total_online': str(entry.total_online),
            'actual_total': str(entry.actual_total),
            'pos_sale': str(entry.pos_sale),
            'over_short': str(entry.over_short),
        }
        current_app.logger.debug(f"Data found: {data}")
    else:
        data = {}
        current_app.logger.debug("No data found for the given Store ID and Date.")

    return jsonify(data)

## Monthly Lottery Page ##


@terminal.route('/monthly_lottery', methods=['GET', 'POST'])
def monthly_lottery():
    form = MonthlyLotteryStoreForm()
    form.store_id.choices = [(store.id, store.name) for store in Store.query.all()]
    lottery_expense_entries = []
    entries = []

    # Variables for calculations
    total_sales = Decimal('0.0')
    commissions = Decimal('0.0')
    total_paid = Decimal('0.0')
    difference = Decimal('0.0')
    total_scratch_off = Decimal('0.0')
    total_online = Decimal('0.0')
    total_actual = Decimal('0.0')
    total_pos_sale = Decimal('0.0')
    total_over_short = Decimal('0.0')

    if form.validate_on_submit():
        # Retrieve form data
        month = int(form.month.data)
        year = int(form.year.data)
        selected_store_id = form.store_id.data
        
        # Calculate start and end dates
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)  # January of the next year
        else:
            end_date = datetime(year, month + 1, 1)

        # Get lottery transactions for the month
        lottery_expense_entries = get_lottery_expense_entries(month, year, selected_store_id)
        
        # Get total lottery expenses for the month
        total_lottery_expenses = calculate_total_lottery_expenses(month, year, selected_store_id)
            
        # Query the database for entries
        entries = DayLotteryEntry.query.filter(
            DayLotteryEntry.date >= start_date,
            DayLotteryEntry.date < end_date,
            DayLotteryEntry.store_id == selected_store_id
        ).order_by(DayLotteryEntry.date).all()

        # Calculate totals
        for entry in entries:
            total_sales += entry.actual_total
            total_scratch_off += entry.total_scratch_off
            total_online += entry.total_online
            total_actual += entry.actual_total
            total_pos_sale += entry.pos_sale
            total_over_short += entry.over_short

        # Calculate commissions
        commissions = total_sales * Decimal('0.05')  # 5% commission

        # Calculate difference
        total_paid = total_lottery_expenses  # Initialize with a default value
        difference = total_sales - total_paid
        
    # For initial page load or if form is not submitted
    return render_template('monthly_lottery.html', form=form, entries=entries, lottery_expense_entries=lottery_expense_entries,
                           total_sales=total_sales, commissions=commissions,
                           total_paid=total_paid, difference=difference,
                           total_scratch_off=total_scratch_off, total_online=total_online,
                           total_actual=total_actual, total_pos_sale=total_pos_sale,
                           total_over_short=total_over_short,)


def get_lottery_expense_entries(selected_month, selected_year, selected_store_id):
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month + 1, 1) if selected_month < 12 else datetime(selected_year + 1, 1, 1)

    lottery_expenses = Expense.query.filter(
        func.extract('year', Expense.expense_date) == selected_year,
        func.extract('month', Expense.expense_date) == selected_month,
        Expense.expense_type == 'Lottery',
        Expense.store_id == selected_store_id
    ).order_by(Expense.expense_date).all()

    return [{'date': expense.expense_date, 'amount': expense.expense_amount} for expense in lottery_expenses]

def calculate_total_lottery_expenses(selected_month, selected_year, selected_store_id):
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month + 1, 1) if selected_month < 12 else datetime(selected_year + 1, 1, 1)

    total_lottery_expenses = db.session.query(func.sum(Expense.expense_amount)).filter(
        func.extract('year', Expense.expense_date) == selected_year,
        func.extract('month', Expense.expense_date) == selected_month,
        Expense.expense_type == 'Lottery',
        Expense.store_id == selected_store_id
    ).scalar() or Decimal('0.0')

    return total_lottery_expenses

## <-------  Lottery Entry and Report End --------> ##