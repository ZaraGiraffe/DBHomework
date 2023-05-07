from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session

from CreateTables import create_all_tables
from CreateTables import columns
from CreateTables import columns_primary

import pandas as pd

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
    params = {"classes": tuple(columns.keys())}

    if "info" in session:
        params["info"] = session["info"]
        params["info_bool"] = True
        session.pop("info")
    else:
        params["info_bool"] = False
    
    if "table" in session:
        params["headers"] = session["headers"]
        params["table"] = session["table"]
        params["data_bool"] = True
        session.pop("table")
        session.pop("headers")
    else:
        params["data_bool"] = False

    return render_template("home.html", **params)


@app.route("/insert_student", methods=["POST"])
def insert_student_func():
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone = request.form["phone"]
    info = f"Succesfully inserted a student {name}"
    try:
        query = f"INSERT INTO students (Name, Surname, Email, Phone) " + \
                f"VALUES ('{name}', '{surname}', '{email}', '{phone}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")


@app.route("/insert_group", methods=["POST"])
def insert_group_func():
    name = request.form["name"]
    course = request.form["course"]
    info = f"Succesfully inserted a group {name}"
    try:
        query = f"INSERT INTO groups (Name, Course) " + \
                f"VALUES ('{name}', '{course}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")


@app.route("/insert_faculty", methods=["POST"])
def insert_faculty_func():
    name = request.form["name"]
    location = request.form["location"]
    info = f"Succesfully inserted a faculty {name}"
    try:
        query = f"INSERT INTO faculties (Name, Location) " + \
                f"VALUES ('{name}', '{location}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")


@app.route("/insert_course", methods=["POST"])
def insert_course_func():
    name = request.form["name"]
    level = request.form["level"]
    info = f"Succesfully inserted a course {name}"
    try:
        query = f"INSERT INTO courses (Name, Level) " + \
                f"VALUES ('{name}', '{level}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")


@app.route("/insert_professor", methods=["POST"])
def insert_professor_func():
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone = request.form["phone"]
    info = f"Succesfully inserted a professor {name}"
    try:
        query = f"INSERT INTO professors (Name, Surname, Email, Phone) " + \
                f"VALUES ('{name}', '{surname}', '{email}', '{phone}')"
        cur.execute(query)
    except Exception as ex:
        info = f"Error: wrong format of input"
    session["info"] = info
    return redirect("/")


@app.route("/get_all", methods=["POST"])
def get_all_func():
    try:
        clas = request.form["class"]
        query = f"SELECT * FROM {clas}"
    except:
        session["info"] = "You didn't select a class"
        return redirect("/")
    cur.execute(query)
    df = pd.DataFrame(columns=columns[clas])
    for k, v in enumerate(cur.fetchall()):
        df.loc[k] = v
    for col in df.columns:
        if col.startswith("FK"):
            df = df.drop(columns=[col])
    session["table"] = [list(i) for i in df.to_numpy()]
    session["headers"] = list(filter(lambda x: not x.startswith("FK"), columns[clas]))
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete_func():
    try:
        clas = request.form["class"]
    except:
        session["info"] = "You didn't select a class" 
        return redirect("/")
    delete_id = request.form["id"]
    try:
        cur.execute(f"DELETE FROM {clas} WHERE {columns_primary[clas]}={delete_id}")
    except:
        session["info"] = "Something wrong with id"
        return redirect("/")
    session["info"] = f"Succesfully deleted an entry"
    return redirect("/")


@app.route("/student_to_group", methods=["POST"])
def student_to_group_func():
    studentID = request.form["studentID"]
    groupID = request.form["groupID"]
    try:
        cur.execute(f"UPDATE students SET FK_GroupID={groupID} WHERE StudentID={studentID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["info"] = "You have added student to a group"
    return redirect("/")


@app.route("/group_to_faculty", methods=["POST"])
def group_to_faculty_func():
    groupID = request.form["groupID"]
    facultyID = request.form["facultyID"]
    try:
        cur.execute(f"UPDATE groups SET FK_FacultyID={facultyID} WHERE GroupID={groupID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["info"] = "You have added group to a faculty"
    return redirect("/")


@app.route("/course_to_professor", methods=["POST"])
def course_to_professor_func():
    courseID = request.form["courseID"]
    professorID = request.form["professorID"]
    try:
        cur.execute(f"UPDATE courses SET FK_ProfessorID={professorID} WHERE CourseID={courseID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["info"] = "You have added course to a professor"
    return redirect("/")


@app.route("/course_to_group", methods=["POST"])
def course_to_group_func():
    courseID = request.form["courseID"]
    groupID = request.form["groupID"]
    try:
        cur.execute(f"UPDATE courses SET FK_GroupID={groupID} WHERE CourseID={courseID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["info"] = "You have added course to a group"
    return redirect("/")


@app.route("/students_in_group", methods=["POST"])
def students_in_group_func():
    groupID = request.form["groupID"]
    mycolumns = list(filter(lambda x: not x.startswith("FK"), columns["students"]))
    string = ", ".join(mycolumns)
    print(string, file=sys.stderr)
    try:
        cur.execute(f"SELECT {string} FROM students WHERE students.FK_GroupID={groupID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["table"] = cur.fetchall()
    session["headers"] = mycolumns
    return redirect("/")

@app.route("/courses_in_group", methods=["POST"])
def courses_in_group_func():
    groupID = request.form["groupID"]
    mycolumns = list(filter(lambda x: not x.startswith("FK"), columns["courses"]))
    string = ", ".join(mycolumns)
    try:
        cur.execute(f"SELECT {string} FROM courses WHERE courses.FK_GroupID={groupID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["table"] = cur.fetchall()
    session["headers"] = mycolumns
    return redirect("/")


@app.route("/group_of_student", methods=["POST"])
def group_of_student_func():
    studentID = request.form["studentID"]
    try:
        cur.execute(f"SELECT FK_GroupID FROM students WHERE StudentID={studentID}")
        groupID = cur.fetchall()[0][0]
        print(groupID, file=sys.stderr)
        if not groupID:
            session["info"] = "Student doesn't have group"
            return redirect("/")
        cur.execute(f"SELECT * FROM groups WHERE groups.GroupID={groupID}")
    except:
        session["info"] = "Something wrong with ID"
        return redirect("/")
    session["table"] = cur.fetchall()
    session["headers"] = list(filter(lambda x: not x.startswith("FK"), columns["groups"]))
    return redirect("/")