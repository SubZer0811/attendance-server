import sqlite3
import os
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, String, Integer, Date
import sqlalchemy
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

class Class(declarative_base(),db.Model):
    class_id = db.Column(db.Integer, primary_key=True)
    faculty = db.Column(db.String)
    class_name = db.Column(db.String)

class StudentClass(declarative_base(),db.Model):
    class_id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer,primary_key=True)

class Attendance(declarative_base(),db.Model):
    date = Column(Date,primary_key=True)
    class_id = Column(Integer,primary_key=True)
    stud_id = Column(Integer,primary_key=True)
    Attendance = Column(Integer) # TODO: Need to change this to boolean

def get_class_id(class_name:str, faculty_id):
    res = Class.query.filter_by(class_name=class_name,faculty=faculty_id).first()
    return res.class_id