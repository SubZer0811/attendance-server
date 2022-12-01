import sqlite3
import os
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, String, Integer, Date, DateTime
import sqlalchemy
import pandas as pd
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
    date = Column(DateTime,primary_key=True)
    class_id = Column(Integer,primary_key=True)
    stud_id = Column(Integer,primary_key=True)
    present = Column(Integer) # TODO: Need to change this to boolean

class ActiveAttendance(declarative_base(),db.Model):
    class_id = Column(Integer,primary_key=True)
    start_timestamp = Column(Integer)
    end_timestamp = Column(Integer)
    qr_text = Column(String)

class PastAttendance(declarative_base(),db.Model):
    class_id = Column(Integer,primary_key=True)
    datetime = Column(DateTime,primary_key=True)

class ClassRoom(declarative_base(),db.Model):
    room_name = Column(String,primary_key=True)
    gps_coord_1 = Column(String)
    gps_coord_2 = Column(String)
    gps_coord_3 = Column(String)
    gps_coord_4 = Column(String)


def get_class_id(class_name:str, faculty_id):
    res = Class.query.filter_by(class_name=class_name,faculty=faculty_id).first()
    return res.class_id

def get_attendance_report(class_id:int):
    query = db.session.query(StudentClass.student_id,User.username,User.full_name,StudentClass.class_id).filter_by(class_id=class_id).join(User,User.username==StudentClass.student_id).all()
    stud_list = [(i[0], i[2]) for i in query]
    # print(f"{stud_list=}")

    datetimes = [i.datetime for i in PastAttendance.query.filter_by(class_id=class_id)]
    # print(f"{datetimes=}")
    df = pd.DataFrame(columns=["Students"]+datetimes+["Percentage"])
    # print(list(df.columns))

    for stud in stud_list:
        row = {"Students":stud[1]}
        count = 0
        for dt in datetimes:
            res = Attendance.query.filter_by(class_id=class_id,stud_id=stud[0],date=dt).first()
            if not res:
                row[dt] = 0
            else:
                row[dt] = res.present
                count += res.present
        
        row["Percentage"] = 0 if not len(datetimes) else (count/len(datetimes))
        row = pd.DataFrame(row,index=[0])

        # print(f"{row=}")
        df = pd.concat([df,row], ignore_index=True)

    df["Percentage"] = df["Percentage"].apply(lambda x: format(float(x),".2f"))
    print(df)
    return df