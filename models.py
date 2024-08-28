from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime, timezone

class Requests(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    courseSection = db.Column(db.String(120), nullable=False)
    dateAdded = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    found = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return {
            "email": self.email
        }

