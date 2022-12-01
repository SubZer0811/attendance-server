from app import User, ClassRoom, db, app
import os

def init_db():
    if not os.path.exists("instance/database.db"):
        with app.app_context():
            print("Database does not exist!")
            print("Creating database...")
            db.create_all()
            db.session.add(User(username='admin', password='admin', full_name='Admin Administrator', role=0))  # type: ignore
            db.session.add(User(username='FAC1', password='FAC1', full_name='Professor X', role=1))  # type: ignore
            db.session.add(User(username='CED18I051', password='password', full_name='Subash Mylraj', role=2))  # type: ignore
            db.session.add(User(username='CED18I100', password='password', full_name='Sachin Dhon', role=2))  # type: ignore
            db.session.add(ClassRoom(room_name="Academic Block", gps_coord_1="12.838525690782836,80.13738919007415", gps_coord_2="12.838933654511866,80.13736773240203", gps_coord_3="12.838923193911707,80.1366596292221", gps_coord_4="12.838619836317529,80.1366596292221"))
            db.session.add(ClassRoom(room_name="Lab Block", gps_coord_1="12.838572763554584,80.13859081971282", gps_coord_2="12.839561289725426,80.13855326878661", gps_coord_3="12.839532523145659,80.13779688584441", gps_coord_4="12.838585839322954,80.13764668213958"))
            db.session.add(ClassRoom(room_name="Admin Block", gps_coord_1="12.839111484648125,80.1377056907379", gps_coord_2="12.839956176077385,80.13767350422972", gps_coord_3="12.839956176077385,80.13744283425444", gps_coord_4="12.839111484648125,80.13744551646346"))
            db.session.add(ClassRoom(room_name="Ashwatha", gps_coord_1="12.835252803960799,80.13542178976172", gps_coord_2="12.835268495089933,80.1364088426792", gps_coord_3="12.835120736918395,80.1364075015747", gps_coord_4="12.835098507805423,80.13551298486823"))
            db.session.commit()
            print("Database Created!")
        
init_db()