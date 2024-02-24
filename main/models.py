from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from database import db

class JobPost(db.Model):
    __tablename__ = 'job_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    job_post_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    education = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(200), nullable=False)
    reference = db.Column(db.String(200))
    resume_filename = db.Column(db.String(255))  # Store the filename or Google Drive link
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
