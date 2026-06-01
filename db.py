import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="student_result_db"
    )

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(name, roll_no, email, department, semester):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, roll_no, email, department, semester) VALUES (%s, %s, %s, %s, %s)",
        (name, roll_no, email, department, semester)
    )
    conn.commit()
    conn.close()

def add_result(student_id, subject_id, marks, exam_year):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (student_id, subject_id, marks, exam_year) VALUES (%s, %s, %s, %s)",
        (student_id, subject_id, marks, exam_year)
    )
    conn.commit()
    conn.close()

def get_results_with_names():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.name as student_name, sub.name as subject_name,
            r.marks, r.grade
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN subjects sub ON r.subject_id = sub.id
        ORDER BY s.name
    """)
    results = cursor.fetchall()
    conn.close()
    return results