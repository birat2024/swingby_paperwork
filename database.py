

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define association table for the many-to-many relationship
user_store_association = db.Table('user_store_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('store_id', db.Integer, db.ForeignKey('store_name.id'))
)
