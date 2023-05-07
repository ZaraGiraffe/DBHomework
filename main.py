from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from CreateTables import create_all_tables

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

create_all_tables(cur)

@app.route("/")
def home_func():
    params = {}

    if "info" in session:
        params["info"] = session["info"]
        params["info_bool"] = True
        session.pop("info")
    else:
        params["info_bool"] = False
    
    if "data_students" in session:
        params["data_students"] = session["data_students"]
        params["data_students_bool"] = True
        session.pop("data_students")
    else:
        params["data_students_bool"] = False

    return render_template("home.html", **params)


@app.route("/insert_student", methods=["POST"])
def insert_student_func():
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone = request.form["phone"]
    info = f"Succesfully inserted a student {name}"
    try:
        query = f"INSERT INTO STUDENTS (Name, Surname, Email, Phone) " + \
                f"VALUES ('{name}', '{surname}', '{email}', '{phone}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")

@app.route("/get_all_students", methods=["POST"])
def get_all_students_func():
    query = f"SELECT * FROM STUDENTS"
    cur.execute(query)
    session["data_students"] = cur.fetchall()
    return redirect("/")