from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session

from CreateTables import columns
from CreateTables import columns_primary


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
        database="derevo2"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

conn.autocommit = True
cur = conn.cursor()


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



@app.route("/get_all", methods=["POST"])
def get_all_func():
    try:
        clas = request.form["class"]
        query = f"SELECT * FROM {clas}"
    except:
        session["info"] = "You didn't select a class"
        return redirect("/")
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = columns[clas]
    return redirect("/")


@app.route("/query1", methods=["POST"])
def query1():
    professor = request.form["professor"]
    grade = request.form["course_grade"]
    query = "SELECT DISTINCT c.CourseName " + \
        "FROM courses c " + \
        "INNER JOIN timetable t ON t.FK_CourseId = c.CourseId " + \
        "INNER JOIN professors p ON p.ProfessorId = t.FK_ProfessorId " + \
        "INNER JOIN groups g ON g.GroupId = t.FK_GroupId " + \
        f"WHERE g.Grade = '{grade}' " + \
        f"AND p.ProfessorName IN ('{professor}')"
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["CourseName"]
    return redirect("/")


@app.route("/query2", methods=["POST"])
def query2():
    professor = request.form["professor"]
    query = "SELECT s.StudentName, s.Surname " + \
            "FROM students s " + \
            "INNER JOIN groups g ON g.GroupId = s.Fk_GroupId " + \
            "INNER JOIN timetable t ON t.FK_GroupId = g.GroupId " + \
            "INNER JOIN professors p ON p.ProfessorId = t.FK_ProfessorId " + \
            f"WHERE p.ProfessorName = '{professor}' " 
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["StudentName", "Surname"]
    return redirect("/")


@app.route("/query3", methods=["POST"])
def query3():
    faculty = request.form["faculty"]
    day = request.form["day"]
    query = "SELECT DISTINCT p.ProfessorName, p.Surname " + \
            "FROM professors p " + \
            "INNER JOIN timetable t ON t.FK_ProfessorId = p.ProfessorId " + \
            "INNER JOIN groups g ON g.GroupId = t.FK_GroupId " + \
            "INNER JOIN faculties f ON f.FacultyId = g.FK_FacultyId " + \
            f"WHERE f.FacultyName = '{faculty}' " + \
            f"AND t.LectureDay = '{day}' "
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["ProfessorName", "Surname"]
    return redirect("/")


@app.route("/query4", methods=["POST"])
def query4():
    student = request.form["student"]
    professor = request.form["professor"]
    query = "SELECT DISTINCT c.CourseName " + \
            "FROM courses c " + \
            "INNER JOIN timetable t ON t.FK_CourseId = c.CourseId " + \
            "INNER JOIN professors p ON p.ProfessorId = t.FK_ProfessorId " + \
            "INNER JOIN groups g ON g.GroupId = t.FK_GroupId " + \
            "INNER JOIN students s ON s.FK_GroupId = g.GroupId " + \
            f"WHERE s.Surname = '{student}' " + \
            f"AND p.Surname = '{professor}'"
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["CourseName"]
    return redirect("/")


@app.route("/query5", methods=["POST"])
def query5():
    query = "SELECT g.GroupName, COUNT(*) AS StudentCount " + \
            "FROM groups g " + \
            "INNER JOIN students s ON s.Fk_GroupId = g.GroupId " + \
            "GROUP BY g.GroupId, g.GroupName " + \
            "ORDER BY StudentCount DESC " + \
            "LIMIT 1"
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["GroupName", "StudentCount"]
    return redirect("/")


@app.route("/query6", methods=["POST"])
def query6():
    query = "SELECT DISTINCT p1.Surname, p2.Surname " + \
        "FROM professors p1 " + \
        "INNER JOIN timetable t1 ON t1.FK_ProfessorId = p1.ProfessorId " + \
        "INNER JOIN ( " + \
            "SELECT GROUP_CONCAT(DISTINCT LectureDay ORDER BY LectureDay) AS lecture_days, FK_ProfessorId "+ \
            "FROM timetable " + \
            "GROUP BY FK_ProfessorId " + \
        ") AS t2 ON t2.lecture_days = ( " + \
            "SELECT GROUP_CONCAT(DISTINCT LectureDay ORDER BY LectureDay) "+ \
            "FROM timetable " + \
            "WHERE FK_ProfessorId = p1.ProfessorId " + \
        ") " + \
        "INNER JOIN professors p2 ON p2.ProfessorId = t2.FK_ProfessorId AND p2.ProfessorId != p1.ProfessorId " 
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["Surname1", "Surname2"]
    return redirect("/")


@app.route("/query7", methods=["POST"])
def query7():
    query = "SELECT DISTINCT g1.GroupName, g2.GroupName " + \
            "FROM groups g1 " + \
            "INNER JOIN timetable t1 ON t1.FK_GroupId = g1.GroupId " + \
            "INNER JOIN ( " + \
                "SELECT g.GroupId, GROUP_CONCAT(DISTINCT c.CourseId ORDER BY c.CourseId) AS course_ids " + \
                "FROM groups g " + \
                "INNER JOIN timetable t ON t.FK_GroupId = g.GroupId " + \
                "INNER JOIN courses c ON c.CourseId = t.FK_CourseId " + \
                "GROUP BY g.GroupId " + \
            ") AS g2courses ON g2courses.course_ids = ( " + \
                "SELECT GROUP_CONCAT(DISTINCT c.CourseId ORDER BY c.CourseId) " + \
                "FROM groups g " + \
                "INNER JOIN timetable t ON t.FK_GroupId = g1.GroupId " + \
                "INNER JOIN courses c ON c.CourseId = t.FK_CourseId " + \
                "WHERE g.GroupId = g1.GroupId " + \
            ") " + \
            "INNER JOIN groups g2 ON g2.GroupId = g2courses.GroupId AND g2.GroupId != g1.GroupId "
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["GroupName1", "GroupName2"]
    return redirect("/")


@app.route("/query8", methods=["POST"])
def query8():
    query = "SELECT DISTINCT p1.Surname, p2.Surname " + \
            "FROM professors p1 " + \
            "INNER JOIN timetable t1 ON t1.FK_ProfessorId = p1.ProfessorId " + \
            "INNER JOIN ( " + \
                "SELECT t2.FK_ProfessorId, GROUP_CONCAT(DISTINCT t2.FK_GroupId ORDER BY t2.FK_GroupId) AS group_ids " + \
                "FROM timetable t2 " + \
                "GROUP BY t2.FK_ProfessorId " + \
            ") AS t2groups ON t2groups.group_ids = ( " + \
                "SELECT GROUP_CONCAT(DISTINCT t3.FK_GroupId ORDER BY t3.FK_GroupId) " + \
                "FROM timetable t3 " + \
                "WHERE t3.FK_ProfessorId = p1.ProfessorId " + \
            ") " + \
            "INNER JOIN professors p2 ON p2.ProfessorId = t2groups.FK_ProfessorId AND p2.ProfessorId != p1.ProfessorId " 

    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["Surname1", "Surname2"]
    return redirect("/")
