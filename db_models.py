import sqlite3
import os
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
# from app import db

db = SQLAlchemy()
class User(UserMixin, db.Model):  # type: ignore
    # primary keys are required by SQLAlchemy
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String(100))
    full_name = db.Column(db.String(100))
    role = db.Column(db.Integer)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False