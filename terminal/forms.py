
import calendar
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DateTimeField, FileField, IntegerField, FloatField, FormField, FieldList, HiddenField, RadioField, SelectField, StringField, SubmitField, DecimalField, TextAreaField, TimeField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Email, InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired




class LotteryEntryForm(FlaskForm):
    row_number_entry = IntegerField('Row Number Entry')  # Add this field to the form
    amount = DecimalField('Amount', validators=[Optional()], default=0)
    begin_day = IntegerField('Begin Day', validators=[Optional()], default=0)
    end_day = IntegerField('End Day', validators=[Optional()], default=0)
    sold = IntegerField('Sold', validators=[Optional()], default=0)
    total = DecimalField('Total', validators=[Optional()], default=0)

class LotteryForm(FlaskForm):
    expense_date = DateField('Expense Date', format='%Y-%m-%d', validators=[DataRequired()])
    selected_store = SelectField('Select Store', coerce=int, validators=[DataRequired()])
    entries = FieldList(FormField(LotteryEntryForm), min_entries=40)
    overwrite = BooleanField('Overwrite', default=False)


    submit = SubmitField('Submit Lottery')


class DayLotteryEntryForm(FlaskForm):
    expense_date = DateField('Expense Date', format='%Y-%m-%d', validators=[DataRequired()])
    selected_store = SelectField('Select Store', coerce=int, validators=[DataRequired()])
    total_scratch_off = DecimalField('Total Scratch Off', validators=[InputRequired()])
    total_online = DecimalField('Total Online', validators=[InputRequired()])
    actual_total = DecimalField('Actual Total', validators=[InputRequired()])
    pos_sale = DecimalField('POS Sale', validators=[InputRequired()])
    over_short = DecimalField('Over/Short', validators=[InputRequired()])
    overwrite = BooleanField("Overwrite existing entry?")


class MonthlyLotteryStoreForm(FlaskForm):
    month = SelectField('Month', choices=[(str(i), datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)], coerce=int)
    year = IntegerField('Year', validators=[NumberRange(min=2000, max=datetime.now().year)])
    store_id = SelectField('Store', coerce=int)  # Ensure this field exists


class MonthlyPaperworkForm(FlaskForm):
    selected_month = SelectField('Month', choices=[(1, 'January'), (2, 'February'), (12, 'December')], coerce=int, validators=[DataRequired()])
    selected_year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    selected_store = SelectField('Store', coerce=int, validators=[DataRequired()]) # Populate choices dynamically based on available stores

    # Add other fields as necessary


class ExpenseForm(FlaskForm):
    expense_date = DateField('Expense Date', validators=[DataRequired()])
    expense_type = SelectField('Expense Type', choices=[], validators=[DataRequired()])  # choices will be populated in the route
    expense_description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    expense_amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    expense_pay_type = SelectField('Payment Type', choices=[], validators=[DataRequired()])  # choices will be populated in the route


class PurchaseOrderForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    po_number = StringField('PO Number', validators=[DataRequired(), Length(max=20)])
    vendor_name = StringField('Vendor Name', validators=[DataRequired(), Length(max=100)])
    invoice_total = DecimalField('Invoice Total', validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField('Payment Method', choices=[], validators=[DataRequired()])
    received_by = StringField('Received By', validators=[DataRequired(), Length(max=100)])
    store_id = SelectField('Store', coerce=int, validators=[DataRequired()])  # Populate choices in the route


class StoreTransferForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    transfer_number = StringField('Transfer Number', validators=[DataRequired()])
    transferred_from = SelectField('Transferred From', choices=[], validators=[DataRequired()])
    transferred_to = SelectField('Transferred To', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    remark = TextAreaField('Remark')
    overwrite = BooleanField('Overwrite')


    def set_store_choices(self, store_choices):
        self.transferred_from.choices = store_choices
        self.transferred_to.choices = store_choices


class TotalPurchaseOrderForm(FlaskForm):
    selected_month = SelectField('Month', choices=[(1, 'January'), (2, 'February')], validators=[DataRequired()])
    selected_year = SelectField('Year', choices=[(2024, '2024'), (2023, '2023')], validators=[DataRequired()])
    selected_store = SelectField('Store', choices=[], validators=[DataRequired()])

class DailySalesForm(FlaskForm):
    selected_month = SelectField('Month', choices=[], validators=[DataRequired()])
    selected_year = SelectField('Year', choices=[], validators=[DataRequired()])
    selected_store = SelectField('Store', choices=[], coerce=int)
    submit = SubmitField('Submit')

class TExpensesForm(FlaskForm):

    selected_month = SelectField('Month', choices=[], validators=[DataRequired()])
    selected_year = SelectField('Year', choices=[], validators=[DataRequired()])
    selected_store = SelectField('Store', choices=[], coerce=int)
    submit = SubmitField('Submit')

class TStoreTransferForm(FlaskForm):
    selected_month = SelectField('Month', choices=[(str(i), calendar.month_name[i]) for i in range(1, 13)], validators=[DataRequired()])
    selected_year = SelectField('Year', choices=[(str(year), str(year)) for year in range(datetime.now().year - 10, datetime.now().year + 1)], validators=[DataRequired()])
    selected_store = SelectField('Store', choices=[], coerce=int)  # Choices to be populated in the route
    submit = SubmitField('Submit')    



class DailySalesSubmitForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    selected_store = SelectField('Store', coerce=int, validators=[DataRequired()])
    name_employee = SelectField('Employee', choices=[])
    hours_employee = FloatField('Hours Worked', validators=[Optional()])
    name_employee1 = SelectField('Employee 1', choices=[])
    hours_employee1 = FloatField('Hours Worked 1', validators=[Optional()])
    name_employee2 = SelectField('Employee 2', choices=[])
    hours_employee2 = FloatField('Hours Worked 2', validators=[Optional()])
    total_sales_shift1 = FloatField('Total Sales Shift 1', validators=[Optional()])
    total_sales_shift2 = FloatField('Total Sales Shift 2', validators=[Optional()])
    card_total_shift1 = FloatField('Card Total Shift 1', validators=[Optional()])
    card_total_shift2 = FloatField('Card Total Shift 2', validators=[Optional()])
    drop_total_shift1 = FloatField('Drop Total Shift 1', validators=[Optional()])
    drop_total_shift2 = FloatField('Drop Total Shift 2', validators=[Optional()])
    lotto_payout_shift1 = FloatField('Lotto Payout Shift 1', validators=[Optional()])
    lotto_payout_shift2 = FloatField('Lotto Payout Shift 2', validators=[Optional()])
    payout1_shift1 = FloatField('Payout 1 Shift 1', validators=[Optional()])
    payout1_shift2 = FloatField('Payout 1 Shift 2', validators=[Optional()])
    payout2_shift1 = FloatField('Payout 2 Shift 1', validators=[Optional()])
    payout2_shift2 = FloatField('Payout 2 Shift 2', validators=[Optional()])
    total_sales_day = FloatField('Total Sales Day', validators=[Optional()])
    card_total_day = FloatField('Card Total Day', validators=[Optional()])
    drop_total_day = FloatField('Drop Total Day', validators=[Optional()])
    lotto_payout_day = FloatField('Lotto Payout Day', validators=[Optional()])
    payout1_day = FloatField('Payout 1 Day', validators=[Optional()])
    payout2_day = FloatField('Payout 2 Day', validators=[Optional()])
    over_short = FloatField('Over/Short', validators=[Optional()])
    bonus_for_day = BooleanField('Bonus for All Employees')

    overwrite = BooleanField('Overwrite')
    submit = SubmitField('Submit')


class EmployeeIntakeForm(FlaskForm):
    # Personal Information
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%m/%d/%Y', validators=[Optional()])
    address = TextAreaField('Address', validators=[DataRequired()])

    # Employment Type
    employment_type = SelectField('Employment Type', choices=[('full_time', 'Full-Time'), ('part_time', 'Part-Time'), ('contract', 'Contract')])

    # Educational Background
    degree = StringField('Degree / Course', validators=[DataRequired()])
    university = StringField('University / Institute', validators=[Optional()])
    year_of_graduate = StringField('Year of Graduate', validators=[Optional()])
    grade = StringField('Grade', validators=[Optional()])

    # Employment History
    company = StringField('Company', validators=[Optional()])
    position = StringField('Position', validators=[Optional()])
    year = StringField('Year', validators=[Optional()])
    reason_for_leaving = TextAreaField('Reason for Leaving', validators=[Optional()])



    # References
    reference_name = StringField('Reference Name', validators=[Optional()])
    reference_phone = StringField('Reference Phone', validators=[Optional()])
    reference_relation = StringField('Relationship to Reference', validators=[Optional()])

    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional()])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional()])

    # Availability
    availability_start_date = DateField('Available Start Date', format='%m/%d/%Y', validators=[Optional()])
    # Skills & Training
    skill = StringField('Skill & Training', validators=[Optional()])
    achievement = StringField('Achievement(s)', validators=[Optional()])
    level = StringField('Level', validators=[Optional()])
    year_of_training = StringField('Year', validators=[Optional()])
    institute = StringField('Institute', validators=[Optional()]) 

    submit = SubmitField('Submit Application')


   

    # Add more fields as needed



def generate_time_choices(interval=30):
    """Generate time choices in HH:MM format with a specified interval in minutes."""
    time_choices = []
    for hour in range(24):
        for minute in range(0, 60, interval):
            time_choices.append((f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}'))
    return time_choices

class DailyScheduleForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    day_choices = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ]
    day = SelectField('Day', choices=day_choices, validators=[DataRequired()])
    employee1 = SelectField('Employee 1', coerce=int)
    employee2 = SelectField('Employee 2', coerce=int)
    employee3 = SelectField('Employee 3', coerce=int)

    # Generate time choices only once and reuse
    time_choices = generate_time_choices(interval=30)
    start1 = SelectField('Start 1', choices=time_choices, validators=[DataRequired()])
    finish1 = SelectField('Finish 1', choices=time_choices, validators=[DataRequired()])
    start2 = SelectField('Start 2', choices=time_choices)
    finish2 = SelectField('Finish 2', choices=time_choices)
    start3 = SelectField('Start 3', choices=time_choices)
    finish3 = SelectField('Finish 3', choices=time_choices)

class ScheduleForm(FlaskForm):
    store_id = SelectField('Store', validators=[DataRequired()], coerce=int)
    daily_schedules = FieldList(FormField(DailyScheduleForm), min_entries=7, max_entries=7)
    submit = SubmitField('Submit')


class ScheduleRetrievalForm(FlaskForm):
    store_id = SelectField('Store', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Retrieve Schedule')





  