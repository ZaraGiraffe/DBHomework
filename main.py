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
    query = "SELECT DISTINCT p1.ProfessorName " + \
            "FROM professors AS p1 " + \
            "WHERE NOT EXISTS ( " + \
            "    SELECT * " + \
            "    FROM ( " + \
            "        SELECT DISTINCT t1.lectureDay AS Days " + \
            "        FROM timetable AS t1 " + \
            "    ) AS alldays " + \
            "    WHERE NOT EXISTS ( " + \
            "        SELECT * " + \
            "        FROM timetable AS t2 " + \
            "        WHERE t2.FK_ProfessorId = p1.ProfessorId " + \
            "        AND t2.LectureDay = alldays.Days " + \
            "    ) " + \
            ")"
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["ProfessorName"]
    return redirect("/")


@app.route("/query7", methods=["POST"])
def query7():
    profname = request.form["professor"]
    query = f"""SELECT distinct p1.ProfessorName
            FROM professors AS p1 
            WHERE NOT EXISTS (
                SELECT * 
                FROM professors AS p2
                INNER JOIN timetable AS t2 ON p2.ProfessorId = t2.FK_ProfessorId
                WHERE p2.ProfessorName = p1.ProfessorName 
                AND EXISTS (
                    SELECT * 
                    FROM professors AS p3
                    INNER JOIN timetable AS t3 ON p3.ProfessorId = t3.FK_ProfessorId
                    WHERE p3.ProfessorName = '{profname}'
                    AND t3.FK_CourseId = t2.FK_CourseId
                )
            )
            """
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["GroupName1", "GroupName2"]
    return redirect("/")


@app.route("/query8", methods=["POST"])
def query8():
    profname = request.form["professor"]
    query = f"""
    SELECT ProfessorName
    FROM (
        SELECT DISTINCT p1.ProfessorName
        FROM professors AS p1 
        INNER JOIN timetable AS t1 ON p1.ProfessorId = t1.FK_ProfessorId
        WHERE t1.FK_GroupId IN (
            SELECT DISTINCT FK_GroupId
            FROM timetable AS t2
            WHERE t2.FK_ProfessorId = (
                SELECT ProfessorId
                FROM professors AS p2
                WHERE p2.ProfessorName = '{profname}'
            )
        )
        AND p1.ProfessorName <> '{profname}'
        GROUP BY p1.ProfessorName
        HAVING COUNT(DISTINCT t1.FK_GroupId) = (
            SELECT COUNT(FK_GroupId)
            FROM timetable AS t3 
            WHERE t3.FK_ProfessorId = (
                SELECT ProfessorId
                FROM professors AS p3
                WHERE p3.ProfessorName = '{profname}'
            )
        ) 
    ) AS dop1
    INNER JOIN (
        SELECT DISTINCT p4.ProfessorName AS professorName2
        FROM professors AS p4
        INNER JOIN timetable AS t4 ON p4.ProfessorId = t4.FK_ProfessorId
        WHERE p4.ProfessorName <> '{profname}'
        AND t4.FK_GroupId NOT IN (
            SELECT DISTINCT FK_GroupId
            FROM timetable t5 
            WHERE t5.FK_ProfessorId = (
                SELECT ProfessorId
                FROM professors AS p5
                WHERE p5.ProfessorName = '{profname}'
            )
        )
    ) AS dop2 ON dop1.ProfessorName = dop2.ProfessorName2
    """
    cur.execute(query)
    session["table"] = cur.fetchall()
    session["headers"] = ["ProfessorName"]
    return redirect("/")
