import datetime
from functools import wraps
import math
import sqlite3
import threading
from time import sleep
import time
import traceback
from flask import flash, jsonify, redirect, render_template, session, url_for, Flask, request
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import sqlalchemy
from pytz import timezone
from sqlalchemy import exc
from shapely.geometry import Point, LinearRing
from shapely.geometry.polygon import Polygon
import pandas as pd

from db_models import PastAttendance, User, Class, StudentClass, Attendance, ActiveAttendance, ClassRoom, db, get_attendance_report, get_class_id

app = Flask(__name__)

app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(minutes=30)
app.config['SERVER_NAME'] = None

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'  # type: ignore
login_manager.init_app(app)

class_timestamp = {}

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not current_user.username:
                    return redirect(url_for('login'))

                elif current_user.role != access_level:
                    return "You do not have access to that page. Sorry!"
            except:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @app.errorhandler(Exception)
# def handle_exception(err):
#     path = request.path
#     print("DEBUG" + path)
#     return path

@login_manager.user_loader
def load_user(username):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(username)

@app.route('/')
def index():
    print(current_user)
    if current_user:
        print("true")
        return home()

    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    full_name = str(data.get('fullname'))
    username = str(data.get('username'))
    password = str(data.get('password'))
    password_rep = str(data.get('password_rep'))
    try:
        role = int(data.get('role'))
    except:
        role = 1

    error_message = ''

    user = User.query.filter_by(username=username).first()
    print(user)
    if user:
        error_message = "Username already exists!"
    if password != password_rep:
        error_message = "Passwords do not match."
    if role == 1 and not username.startswith('FAC'):
        error_message = "Faculty username should start with 'FAC'."
    if re.findall(r"[^a-zA-Z\d\s:]", full_name+username+password):
        error_message = "Fields cannot contain non-alphanumeric characters."

    if error_message:
        print(error_message)
        return jsonify({"error_message": error_message})

    db.session.add(User(username=username, password=password, full_name=full_name, role=role))
    db.session.commit()

    return jsonify({"error_message": "success"})

@app.route('/login')
def login_page():
    print("login_page")
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    print("login")
    data = request.get_json()
    username = str(data.get('username'))
    password = str(data.get('password'))

    user = User.query.filter_by(username=username).first()
    if not user or not (user.password == password):
    # TODO: if not user or not check_password_hash(user.password, password):
        return jsonify({"error_message": "Invalid Credentials!"})

    user.authenticated = True
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({"error_message": "success"})

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return "You are logged out!"

@app.route('/home')
@login_required
def home():
    if current_user.role == 0:
        return room()
    elif current_user.role == 1:
        print(current_user.role)
        classes = [(i.class_id,i.class_name) for i in Class.query.filter_by(faculty=current_user.username)]
        print(classes)

        return render_template(
            'home.html',
            classes=classes
        )
    return render_template('login.html')

@app.route('/class/<int:class_id>')
@login_required
def get_class(class_id):
    res = db.session.query(Class.class_id,Class.class_name).filter_by(class_id=class_id,faculty=current_user.username).first()
    if not res:
        return "Invalid class_id!"

    class_id, class_name = res

    df = get_attendance_report(class_id)
    cols = df.columns
    print([str(i) for i in cols.to_list()])
    print(df.to_numpy())

    return render_template(
        "class.html",
        class_id=class_id,
        class_name=class_name,
        cols=cols,
        rows=df.to_numpy()
    )


@app.route('/new_class')
@login_required
def new_class():
    return render_template('new_class.html')

@app.route('/new_class', methods=['POST'])
@login_required
def new_class_form():
    class_name = str(request.form.get('class_name'))
    stud_list = str(request.form.get('students_list'))
    
    db.session.add(Class(
        faculty=current_user.username,
        class_name=class_name
    ))
    db.session.commit()
    class_id = get_class_id(class_name,current_user.username)

    stud_list = stud_list.splitlines()
    rows = [StudentClass(class_id=class_id,student_id=i) for i in stud_list]
    db.session.add_all(rows)
    db.session.commit()

    return redirect(f"/class/{class_id}")

@app.route('/add_studs/<int:class_id>', methods=['POST'])
@login_required
def add_students(class_id):
    res = db.session.query(Class.class_id,Class.class_name).filter_by(class_id=class_id,faculty=current_user.username).first()
    if not res:
        return "Invalid class_id!"

    stud_list = str(request.form.get('students_list'))
    stud_list = stud_list.splitlines()
    rows = [StudentClass(class_id=class_id,student_id=i) for i in stud_list]
    db.session.add_all(rows)
    db.session.commit()

    return redirect(f'/class/{class_id}')

@app.route('/attendance/<int:class_id>', methods=['POST'])
@login_required
def attendance(class_id):
    res = db.session.query(Class.class_id,Class.class_name).filter_by(class_id=class_id,faculty=current_user.username).first()
    if not res:
        return "Invalid class_id!"

    class_id, class_name = res

    class_rooms = [i.room_name for i in db.session.query(ClassRoom.room_name)]
    print(class_rooms)
    return render_template("attendance.html",
        class_id=class_id,
        class_name=class_name,
        class_rooms=class_rooms)

@app.route('/take_attendance/<int:class_id>', methods=['POST'])
@login_required
def take_attendance(class_id):
    res = db.session.query(Class.class_id,Class.class_name).filter_by(class_id=class_id,faculty=current_user.username).first()
    if not res:
        return "Invalid class_id!"

    class_id, class_name = res
    data = request.get_json()
    class_room = data.get("classroom")
    print(data)
    
    act_atdn = db.session.query(ActiveAttendance).filter_by(class_id=class_id).first()
    # Check if an active attendance is available for the given class id
    if not act_atdn:
        if data['msg'] == "start":
            duration = 60 # in seconds
            date_time = datetime.datetime.now(timezone("Asia/Kolkata"))
            start_timestamp = time.mktime(date_time.timetuple())
            end_timestamp = start_timestamp + duration
            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
            
            qr_text = f"{class_id}_{start_timestamp}_{end_timestamp}_{class_room}"
            db.session.add(ActiveAttendance(class_id=class_id, start_timestamp=start_timestamp, end_timestamp=end_timestamp, qr_text=qr_text))
            db.session.commit()

            thread = threading.Thread(target=timer,args=[class_id,])
            thread.start()
            act_atdn = db.session.query(ActiveAttendance).filter_by(class_id=class_id).first()


            return jsonify({
                "msg": "success",
                "qr_text": act_atdn.qr_text,
                "time_left": act_atdn.end_timestamp - time.mktime(datetime.datetime.now(timezone("Asia/Kolkata")).timetuple())
            })

        elif data['msg'] == "heartbeat":
            return jsonify({
                "msg": "Time's up!",
                "time_left": -1
            })
    if data['msg'] == "start":
        return jsonify({
                "msg": "success",
                "qr_text": act_atdn.qr_text,
                "time_left": act_atdn.end_timestamp - time.mktime(datetime.datetime.now(timezone("Asia/Kolkata")).timetuple())
            })
    if data['msg'] == "heartbeat":
        return jsonify({
        "msg": "success",
        "qr_text": act_atdn.qr_text,
        "time_left": act_atdn.end_timestamp - time.mktime(datetime.datetime.now(timezone("Asia/Kolkata")).timetuple())
        })
    else:
        return jsonify({
        "msg": "not started"
        })

@app.route("/punch_attendance", methods=["POST"])
@login_required
def punch_attendance():

    print(request.headers)
    data = request.get_json()
    print(data)
    qr_text = str(data.get("qr_text"))
    stud_id = str(data.get("username"))
    timestamp = int(data.get("timestamp"))
    latitude = float(data.get("latitude"))
    longitude = float(data.get("longitude"))
    message = ""
    
    try:
        class_id, start_timestamp, end_timestamp, class_room = qr_text.split("_")
        print(class_id, start_timestamp, end_timestamp)
        act_atdn = db.session.query(ActiveAttendance).filter_by(class_id=class_id).first()
        if not act_atdn:
            message = "Invalid QR! (Error Code: QR10001)"
        elif not (act_atdn.qr_text == qr_text):
            message = "Invalid QR! (Error Code: QR10002)"
        elif timestamp > act_atdn.end_timestamp:
            message = "Time's up! No Attendance!"
        elif not inside_classroom(class_room, (latitude, longitude)):
            message = "You are not inside the classroom!"
        else:
            db.session.add(Attendance(date=datetime.datetime.fromtimestamp(act_atdn.end_timestamp), class_id=class_id, stud_id=stud_id, present=1))
            db.session.commit()
            message = "Attendance Punched"
    except exc.IntegrityError:
        message = "Attendance already punched"
    except Exception:
        traceback.print_exc()
        message = "Invalid QR!"

    return jsonify({
        "message": message
    })

@app.route("/create_room", methods=["POST"])
def create_room():
    data = request.get_json()
    room_name = str(data.get("room_name"))
    gps_coord_1 = str(data.get("gps_coord_1"))
    gps_coord_2 = str(data.get("gps_coord_2"))
    gps_coord_3 = str(data.get("gps_coord_3"))
    gps_coord_4 = str(data.get("gps_coord_4"))

    message = "success"
    try:
        db.session.add(ClassRoom(
            room_name=room_name,
            gps_coord_1=gps_coord_1,
            gps_coord_2=gps_coord_2,
            gps_coord_3=gps_coord_3,
            gps_coord_4=gps_coord_4
        ))
        db.session.commit()
    except exc.IntegrityError:
        message = "Class Room Number already exists!"

    return jsonify({
        "message": message
    })

@app.route("/room/")
@requires_access_level(0)
def room():
    rooms = [i.room_name for i in db.session.query(ClassRoom)]
    return render_template("room.html", rooms=rooms)

@app.route("/get_room/<string:room_id>", methods=["POST"])
@requires_access_level(0)
def get_room(room_id):
    room = db.session.query(ClassRoom).filter_by(room_name=room_id).first()
    print(room)
    return jsonify({
        "gps_coord_1": room.gps_coord_1,
        "gps_coord_2": room.gps_coord_2,
        "gps_coord_3": room.gps_coord_3,
        "gps_coord_4": room.gps_coord_4
    })

@app.route("/change_room/<string:room_id>", methods=["POST"])
@requires_access_level(0)
def change_room(room_id):
    data = request.get_json()
    print(data)

    room = db.session.query(ClassRoom).filter_by(room_name=room_id).first()
    room.gps_coord_1 = data.get("gps_coord_1")
    room.gps_coord_2 = data.get("gps_coord_2")
    room.gps_coord_3 = data.get("gps_coord_3")
    room.gps_coord_4 = data.get("gps_coord_4")
    db.session.commit()

    return jsonify("asf")

def timer(class_id):

    with app.app_context():
        act_atdn = db.session.query(ActiveAttendance).filter_by(class_id=class_id).first()

        end_timestamp = act_atdn.end_timestamp
        start_timestamp = act_atdn.start_timestamp
        duration = end_timestamp - start_timestamp
        sleep(duration)

        db.session.delete(act_atdn)
        db.session.add(PastAttendance(class_id=class_id,datetime=datetime.datetime.fromtimestamp(act_atdn.end_timestamp)))
        db.session.commit()


@app.route("/test")
def test():
    return render_template("test.html")

def inside_classroom(class_room, cur_loc):
    coords = [(float(i.split(',')[0]),float(i.split(',')[1])) for i in db.session.query(ClassRoom.gps_coord_1,ClassRoom.gps_coord_2,ClassRoom.gps_coord_3,ClassRoom.gps_coord_4).filter_by(room_name=class_room).first()]

    poly = Polygon(coords)
    point = Point(cur_loc)

    distance = poly.exterior.distance(point)
    return poly.contains(point)
    # print(coords)
    # region = Polygon(coords)
    # point = Point(cur_loc)

    # pol_ext = LinearRing(region.exterior.coords)
    # d = pol_ext.project(point)
    # p = pol_ext.interpolate(d)
    # closest_point_coords = list(p.coords)[0]

    # print(closest_point_coords)
    
    # lon1, lat1, lon2, lat2 = map(math.radians, [point.y, point.x, closest_point_coords[1], closest_point_coords[0]])

    # # haversine formula 
    # dlon = lon2 - lon1 
    # dlat = lat2 - lat1 
    # a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    # c = 2 * math.asin(math.sqrt(a)) 
    # r = 6371 # Radius of earth in kilometers
    # distance = c * r * 1000
    print(distance)
    print(distance < 5)
    return distance < 5

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)