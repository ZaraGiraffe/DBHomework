import sys


columns = {"students": ("StudentID", "Name", "Surname", "Email", "Phone", "FK_GroupID"),
           "courses": ("CourseID", "Name", "Level", "FK_GroupID", "FK_ProfessorID"),
           "faculties": ("FacultyID", "Name", "Location"),
           "groups": ("GroupID", "Name", "Course", "FK_FacultyID"),
           "professors": ("ProfessorID", "Name", "Surname", "Email", "Phone")}

columns_primary = {"students": "StudentID",
           "courses": "CourseID",
           "faculties": "FacultyID",
           "groups": "GroupID",
           "professors": "ProfessorID"}

def create_students(cur):
    query = "CREATE TABLE students (" + \
    "StudentID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Surname varchar(100)," + \
    "Email varchar(100)," + \
    "Phone varchar(100)," + \
    "PRIMARY KEY (StudentID)" + \
    ")"
    try:
        cur.execute("SELECT * FROM students")
    except:
        cur.execute(query)


def create_groups(cur):
    query = "CREATE TABLE groups (" + \
    "GroupID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Course varchar(100)," + \
    "PRIMARY KEY (GroupID)" + \
    ")"
    try:
        cur.execute("SELECT * FROM groups")
    except:
        cur.execute(query)


def create_faculties(cur):
    query = "CREATE TABLE faculties (" + \
    "FacultyID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Location varchar(100)," + \
    "PRIMARY KEY (FacultyID)" + \
    ")"

    try:
        cur.execute("SELECT * FROM faculties")
    except:
        cur.execute(query)


def create_courses(cur):
    query = "CREATE TABLE courses (" + \
    "CourseID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Level varchar(100)," + \
    "PRIMARY KEY (CourseID)" + \
    ")"

    try:
        cur.execute("SELECT * FROM courses")
    except:
        cur.execute(query)


def create_professors(cur):
    query = "CREATE TABLE professors (" + \
    "ProfessorID int NOT NULL AUTO_INCREMENT," + \
    "Name varchar(100)," + \
    "Surname varchar(100)," + \
    "Email varchar(100)," + \
    "Phone varchar(100)," + \
    "PRIMARY KEY (ProfessorID)" + \
    ")"

    try:
        cur.execute("SELECT * FROM professors")
    except:
        cur.execute(query)


def add_foreign_key(cur, clasWhere, IDWhere, clasTo, IDTo):
    query1 = f"ALTER TABLE {clasWhere} " + \
    f"ADD FOREIGN KEY ({IDWhere}) REFERENCES {clasTo}({IDTo})"
    query2 = f"ALTER TABLE {clasWhere} " + \
    f"ADD {IDWhere} int"
    try:
        cur.execute(f"SELECT {IDWhere} FROM {clasWhere}")
    except:
        cur.execute(query2)
        cur.execute(query1)
        print("Error in adding foreign key", file=sys.stderr)


def create_all_tables(cur):
    create_courses(cur)
    create_faculties(cur)
    create_professors(cur)
    create_groups(cur)
    create_students(cur)
    add_foreign_key(cur, "students", "FK_GroupID", "groups", "GroupID")
    add_foreign_key(cur, "groups", "FK_FacultyID", "faculties", "FacultyID")
    add_foreign_key(cur, "courses", "FK_GroupID", "groups", "GroupID")
    add_foreign_key(cur, "courses", "FK_ProfessorID", "professors", "ProfessorID")

