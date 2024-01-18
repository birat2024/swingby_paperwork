import datetime
from flask import Flask, render_template, flash, redirect, request, url_for, session
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, FloatField, Form, SelectField, SubmitField, StringField, PasswordField, TextAreaField, validators
import os
import secrets
from flask_mysqldb import MySQL
import bcrypt
from wtforms.validators import DataRequired, Email, optional
from datetime import datetime
from flask_login import LoginManager




# Create Flask app and configure SQLAlchemy
app = Flask(__name__)


# Generate a random secret key
secret_key = secrets.token_hex(24)
app.secret_key = secret_key

# MySQL Config (you can keep this if needed)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('DB_CONNECTION_STRING')  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'careerwebsite'

mysql = MySQL(app)




@app.route('/lottery_input')
def lottery_input():
    # You can add logic here to pass necessary data to your template
    # For example, if you have lottery data to display, you can fetch it and pass it to the template:
    # lottery_data = fetch_lottery_data()  # This is just a placeholder for your data fetching logic.
    
    return render_template('lottery_input.html')  # Assuming you have a template named 'lottery_input.html'







@app.route('/submit_dailysales', methods=['POST'])
def submit_dailysales():
    form = DailySalesForm()
    if form.validate_on_submit():
        try:
            # Extract data from form
            date = form.date.data
            name_employee = form.name_employee.data
            hours_employee = form.hours_employee.data
            name_employee1 = form.name_employee1.data
            hours_employee1 = form.hours_employee1.data
            name_employee2 = form.name_employee2.data
            hours_employee2 = form.hours_employee2.data
            total_sales_shift1 = form.total_sales_shift1.data
            total_sales_shift2 = form.total_sales_shift2.data
            total_sales_day = form.total_sales_day.data
            card_total_shift1 = form.card_total_shift1.data
            card_total_shift2 = form.card_total_shift2.data
            card_total_day = form.card_total_day.data
            drop_total_shift1 = form.drop_total_shift1.data
            drop_total_shift2 = form.drop_total_shift2.data
            drop_total_day = form.drop_total_day.data
            lotto_payout_shift1 = form.lotto_payout_shift1.data
            lotto_payout_shift2 = form.lotto_payout_shift2.data
            lotto_payout_day = form.lotto_payout_day.data
            payout1_shift1 = form.payout1_shift1.data
            payout1_shift2 = form.payout1_shift2.data
            payout1_day = form.payout1_day.data
            payout2_shift1 = form.payout2_shift1.data
            payout2_shift2 = form.payout2_shift2.data
            payout2_day = form.payout2_day.data
            over_short = form.over_short.data

            # Connect to the database
            cursor = mysql.connection.cursor()

            # SQL query to insert data into the dailysales table
            dailysales_query = """
                INSERT INTO dailysales (
                    date,
                    name_employee, hours_employee,
                    name_employee1, hours_employee1,
                    name_employee2, hours_employee2,
                    total_sales_shift1, total_sales_shift2, total_sales_day,
                    card_total_shift1, card_total_shift2, card_total_day,
                    drop_total_shift1, drop_total_shift2, drop_total_day,
                    lotto_payout_shift1, lotto_payout_shift2, lotto_payout_day,
                    payout1_shift1, payout1_shift2, payout1_day,
                    payout2_shift1, payout2_shift2, payout2_day,
                    over_short
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Execute the dailysales SQL query with the form data
            cursor.execute(dailysales_query, (
                date,
                name_employee, hours_employee,
                name_employee1, hours_employee1,
                name_employee2, hours_employee2,
                total_sales_shift1, total_sales_shift2, total_sales_day,
                card_total_shift1, card_total_shift2, card_total_day,
                drop_total_shift1, drop_total_shift2, drop_total_day,
                lotto_payout_shift1, lotto_payout_shift2, lotto_payout_day,
                payout1_shift1, payout1_shift2, payout1_day,
                payout2_shift1, payout2_shift2, payout2_day,
                over_short
            ))

            # Commit the changes to the dailysales table
            mysql.connection.commit()

            # Flash a success message
            flash('Dailysales data submitted successfully!', 'success')
        except Exception as e:
            # Rollback transaction on error
            mysql.connection.rollback()
            # Flash error message
            flash(f'An error occurred while submitting dailysales data: {e}', 'danger')
        finally:
            # Close the cursor
            cursor.close()

    # Redirect to the dailysales form page
    return redirect(url_for('dailysales'))

@app.route('/dailysales', methods=['GET', 'POST'])
def dailysales():
    form = DailySalesForm()

    
    return render_template('dailysales.html', form=form)


class DailySalesForm(FlaskForm):
    # Date 
    date = StringField('date', validators=[DataRequired()])

    # Fields for Employees
    name_employee = StringField('Employee Name', validators=[DataRequired()])
    hours_employee = FloatField('Employee Hours', validators=[DataRequired()])
    name_employee1 = StringField('Employee 1 Name', validators=[optional()])
    hours_employee1 = FloatField('Employee 1 Hours',validators=[optional()])
    name_employee2 = StringField('Employee 2 Name', validators=[optional()])
    hours_employee2 = FloatField('Employee 2 Hours', validators=[optional()])

    total_sales_shift1 = FloatField('Total Sales Shift 1', validators=[DataRequired()])
    total_sales_shift2 = FloatField('Total Sales Shift 2', validators=[optional()])
    total_sales_day = FloatField('Total Sales Day', validators=[DataRequired()])
    
    card_total_shift1 = FloatField('Card Total Shift 1', validators=[DataRequired()])
    card_total_shift2 = FloatField('Card Total Shift 2', validators=[optional()])
    card_total_day = FloatField('Card Total Day', validators=[DataRequired()])

    drop_total_shift1 = FloatField('Drop Total Shift 1', validators=[DataRequired()])
    drop_total_shift2 = FloatField('Drop Total Shift 2', validators=[optional()])
    drop_total_day = FloatField('Drop Total Day', validators=[DataRequired()])

    lotto_payout_shift1 = FloatField('Lotto Payout Shift 1', validators=[optional()])
    lotto_payout_shift2 = FloatField('Lotto Payout Shift 2', validators=[optional()])
    lotto_payout_day = FloatField('Lotto Payout Day', validators=[optional()])

    payout1_shift1 = FloatField('Payout 1 Shift 1', validators=[optional()])
    payout1_shift2 = FloatField('Payout 1 Shift 2',validators=[optional()])
    payout1_day = FloatField('Payout 1 Day', validators=[optional()])

    payout2_shift1 = FloatField('Payout 2 Shift 1', validators=[optional()])
    payout2_shift2 = FloatField('Payout 2 Shift 2', validators=[optional()])
    payout2_day = FloatField('Payout 2 Day', validators=[optional()])

    over_short = FloatField('Over/Short')

    submit = SubmitField('Submit')

class ExpenseForm(FlaskForm):
    expense_date = DateField('Date', validators=[DataRequired()])
    expense_type = StringField('Expense Type', validators=[DataRequired()])
    expense_description = TextAreaField('Description', validators=[DataRequired()])
    expense_amount = DecimalField('Amount', validators=[DataRequired()])
    expense_pay_type = SelectField('Payment Type', choices=[('cash', 'Cash'), ('credit', 'Credit Card')], validators=[DataRequired()])

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    form = ExpenseForm()
    if form.validate_on_submit():
        # Extract data from the form and insert it into the database
        expense_date = form.expense_date.data
        expense_type = form.expense_type.data
        expense_description = form.expense_description.data
        expense_amount = form.expense_amount.data
        expense_pay_type = form.expense_pay_type.data

        # Insert data into the database (assuming you have a MySQL database connection)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO expenses (expense_date, expense_type, expense_description, expense_amount, expense_pay_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (expense_date, expense_type, expense_description, expense_amount, expense_pay_type))
        mysql.connection.commit()
        cursor.close()
        
        flash("Expense added successfully.", "success")
        return redirect(url_for('expenses'))  # Redirect to the same page after submission

    # Retrieve existing expenses from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 100")  # Adjust the 'ORDER BY' clause as needed
    orders = cursor.fetchall()
    cursor.close()

    return render_template('expenses.html', form=form, expenses=expenses)






@app.route('/search')
def search():
    return render_template('search.html')



## GOOD TILL HERE##
@app.route('/dashboard')
def dashboard():
    # Make sure the user is logged in
    if not is_logged_in():
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('login'))
    else:
    # Your dashboard code here
     return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('index.html')

# AUTHENTICATION #
class SignupForm(FlaskForm):
    name = StringField("Name", validators=[validators.DataRequired()])
    email = StringField("Email", validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("Signup")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Helper function to check login status
def is_logged_in():
    return 'user_id' in session

@app.context_processor
def context_processor():
    return dict(is_logged_in=is_logged_in)

def get_user_email_from_session():
    # Check if the 'user_id' key exists in the session
    if 'user_id' in session:
        # You can retrieve the user's email from your session data
        user_id = session['user_id']
        # Query your database to get the user's email based on the user_id
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user_email = cursor.fetchone()
        cursor.close()
        # Return the user's email
        if user_email:
            return user_email[0]
    return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password before storing it in the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if the user already exists in the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            flash('Email address is already in use. Please use a different email.', 'danger')
        else:
            # Insert the user data into the database
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Retrieve the user's data from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            user_id, stored_hashed_password = user_data

            # Check if the provided password matches the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                # Passwords match, user is authenticated

                # Store the user ID in the session
                session['user_id'] = user_id

                # Redirect to the 'index' route upon successful login
                return redirect(url_for('dashboard'))

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


class StoreTransferForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    transfer_number = StringField('Transfer #', validators=[DataRequired()])
    transferred_from = StringField('Transferred From', validators=[DataRequired()])
    transferred_to = StringField('Transferred To', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    remark = TextAreaField('Remark')
    submit = SubmitField('Submit')

@app.route('/store_transfer', methods=['GET', 'POST'])
def store_transfer():
    form = StoreTransferForm()
    if form.validate_on_submit():
        # Extract data from form
        date = form.date.data
        transfer_number = form.transfer_number.data
        transferred_from = form.transferred_from.data
        transferred_to = form.transferred_to.data
        amount = form.amount.data
        remark = form.remark.data

        # Insert data into database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO store_transfer (date, transfer_number, transferred_from, transferred_to, amount, remark)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (date, transfer_number, transferred_from, transferred_to, amount, remark))
        mysql.connection.commit()
        cursor.close()
        flash("Store Transfer added successfully.", "success")
        return redirect(url_for('store_transfer'))

    # Retrieve existing transfers from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM store_transfer ORDER BY date DESC")
    transfers = cursor.fetchall()
    cursor.close()

    return render_template('store_transfer.html', form=form, transfers=transfers)


class PurchaseOrderForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    po_number = StringField('PO#', validators=[DataRequired()])
    vendor_name = StringField('Vendor Name', validators=[DataRequired()])
    invoice_total = FloatField('Invoice Total', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[('Cash', 'Cash'), ('Credit', 'Credit'), ('Other', 'Other')], validators=[DataRequired()])
    received_by = StringField('Received By', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/purchase_order', methods=['GET', 'POST'])
def purchase_order():
    form = PurchaseOrderForm()
    if form.validate_on_submit():
        date = form.date.data
        po_number = form.po_number.data
        vendor_name = form.vendor_name.data
        invoice_total = form.invoice_total.data
        payment_method = form.payment_method.data
        received_by = form.received_by.data

        # Database Insertion
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO purchase_order (date, po_number, vendor_name, invoice_total, payment_method, received_by) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (date, po_number, vendor_name, invoice_total, payment_method, received_by))
        mysql.connection.commit()
        cursor.close()
        flash("Purchase Order added successfully.", "success")
        return redirect(url_for('purchase_order'))

    # Retrieve existing orders from database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM purchase_order")
    orders = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM purchase_order ORDER BY date DESC LIMIT 100")  # Adjust the 'ORDER BY' clause as needed
    orders = cursor.fetchall()
    cursor.close()


    return render_template('purchase_order.html', form=form, orders=orders)

class JobApplicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    education = StringField('Education', validators=[DataRequired()])
    experience = TextAreaField('Experience', validators=[DataRequired()])
    reference = StringField('Reference')
    submit = SubmitField('Submit')

@app.route('/jobapplication', methods=['GET', 'POST'])
def jobapplication():
    form = JobApplicationForm()
    return render_template('jobapplication.html', form=form)

@app.route('/employee')
def employee():
    return render_template('employee.html')

@app.route('/main_terminal')
def main_terminal():
    return render_template('main_terminal.html')


@app.route('/misc')
def misc():
    return "Hello World"


if __name__ == '__main__':
    app.run(debug=True)


