from flask_wtf import FlaskForm
from wtforms import EmailField, FileField, HiddenField, StringField, TextAreaField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileAllowed, FileRequired


class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    company = StringField('Company Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    job_type = SelectField('Job Type', choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract')])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    qualifications = TextAreaField('Qualifications', validators=[DataRequired()])
    submit = SubmitField('Post Job')

class ApplicationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    education = TextAreaField('Education', validators=[DataRequired()])
    experience = TextAreaField('Experience', validators=[DataRequired()])
    reference = TextAreaField('Reference', validators=[DataRequired()])
    resume = FileField('Upload Resume', validators=[FileRequired()])
    submit = SubmitField('Submit')
