from app import User, db, app
import os

def init_db():
    if not os.path.exists("instance/database.db"):
        with app.app_context():
            print("Database does not exist!")
            print("Creating database...")
            db.create_all()
            db.session.add(User(username='admin', password='admin', full_name='Admin Administrator', role=1))  # type: ignore
            db.session.commit()
            print("Database Created!")
        
init_db()