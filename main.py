from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session

import mariadb
import sys

app = Flask(__name__)
app.secret_key = "key"

try:
    conn = mariadb.connect(
        user="root",
        password="root",
        host="localhost",
        port=3306,
        database="derevo"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

conn.autocommit = True
cur = conn.cursor()

create_table_classes = "CREATE TABLE CLASSES (" + \
    "StudentID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Surname varchar(100)," + \
    "Email varchar(100)," + \
    "Phone varchar(100)," + \
    "PRIMARY KEY (StudentID)" + \
")"

try:
    cur.execute("SELECT * FROM CLASSES")
except:
    cur.execute(create_table_classes)


@app.route("/")
def home_func():
    params = {}
    if "info" in session:
        params["info"] = session["info"]
        params["info_bool"] = True
        session.pop("info")
    else:
        params["info_bool"] = False
    return render_template("home.html", **params)


@app.route("/insert_student", methods=["POST"])
def insert_student_func():
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone = request.form["phone"]
    info = f"Succesfully inserted a student {name}"
    try:
        query = f"INSERT INTO CLASSES (Name, Surname, Email, Phone) " + \
                f"VALUES ('{name}', '{surname}', '{email}', '{phone}')"
        cur.execute(query)
        print(name, surname, email, phone, file = sys.stderr)
    except Exception as ex:
        info = f"Error: wrong format of input"
        print(ex, file = sys.stderr)
    session["info"] = info
    return redirect("/")