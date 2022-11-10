from app import User, db, app
import os

def init_db():
    if not os.path.exists("instance/database.db"):
        with app.app_context():
            print("Database does not exist!")
            print("Creating database...")
            db.create_all()
            db.session.add(User(username='admin', password='admin', full_name='Admin Administrator', role=0))  # type: ignore
            db.session.add(User(username='FAC1', password='FAC1', full_name='Admin Administrator', role=1))  # type: ignore
            db.session.add(User(username='stud1', password='stud1', full_name='Student 1', role=2))  # type: ignore
            db.session.add(User(username='stud2', password='stud2', full_name='Student 2', role=2))  # type: ignore
            db.session.commit()
            print("Database Created!")
        
init_db()