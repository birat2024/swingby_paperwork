

from database import db

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)  # Assuming a simple integer reference to store
    date = db.Column(db.Date, nullable=False)
    day = db.Column(db.String(50), nullable=False)
    employee1 = db.Column(db.String(50), nullable=False)
    start1 = db.Column(db.Time, nullable=False)
    finish1 = db.Column(db.Time, nullable=False)
    employee2 = db.Column(db.String(50), nullable=True)  # Nullable if optional
    start2 = db.Column(db.Time, nullable=True)
    finish2 = db.Column(db.Time, nullable=True)
    employee3 = db.Column(db.String(50), nullable=True)  # Nullable if optional
    start3 = db.Column(db.Time, nullable=True)
    finish3 = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f"<Schedule(store_id={self.store_id}, date={self.date}, day={self.day}, employee1={self.employee1}, start1={self.start1}, finish1={self.finish1})>"
