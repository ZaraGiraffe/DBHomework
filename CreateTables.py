import sys


columns = {"students": ("StudentId", "StudentName", "Surname", "Email", "Phone", "FK_GroupId"),
           "courses": ("CourseId", "CourseName", "Level"),
           "faculties": ("FacultyId", "FacultyName", "Location"),
           "groups": ("GroupId", "GroupName", "Grade", "FK_FacultyId"),
           "professors": ("ProfessorId", "ProfessorName", "Surname", "Email", "Phone"),
           "timetable": ("Fk_GroupId", "Fk_ProfessorId", "FK_CourseId", "TimeTableId", "LectureTime", "LectureDay")}

columns_primary = {"students": "StudentId",
           "courses": "CourseId",
           "faculties": "FacultyId",
           "groups": "GroupId",
           "professors": "ProfessorId",
           "timetable": "TimeTableId"}
