from datetime import datetime
from typing import Required
from flask_wtf import FlaskForm
from wtforms import DateField, DateTimeLocalField, StringField, PasswordField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
import pytz
from pytz import all_timezones




class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('Employee', 'Employee'), ('Manager', 'Manager'), ('Owner', 'Owner')])
    stores = SelectMultipleField('Select Stores')
    submit = SubmitField('Sign Up')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')




class SettingsForm(FlaskForm):
    default_timezone = SelectField('Default Timezone', choices=[], validators=[DataRequired()])  
    submit = SubmitField('Save Settings')

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.default_timezone.choices = [(tz, tz) for tz in pytz.all_timezones]