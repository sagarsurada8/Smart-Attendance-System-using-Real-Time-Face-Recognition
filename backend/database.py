import sqlite3
import os
from datetime import datetime


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE_PATH = os.path.join(
    DATA_DIR,
    "attendance.db"
)


# ============================================================
# GET DATABASE CONNECTION
# ============================================================

def get_connection():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # STUDENTS TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            registration_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ========================================================
    # ATTENDANCE TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)


    connection.commit()
    connection.close()


# ============================================================
# ADD STUDENT
# ============================================================

def add_student(
    roll_number,
    name,
    registration_number=""
):

    create_database()

    roll_number = str(
        roll_number
    ).strip()

    name = str(
        name
    ).strip()

    registration_number = str(
        registration_number
    ).strip()


    if not name or not roll_number:

        return {
            "success": False,
            "message": "Name and roll number are required"
        }


    connection = get_connection()

    cursor = connection.cursor()


    try:

        cursor.execute("""
            INSERT INTO students (
                name,
                roll_number,
                registration_number
            )
            VALUES (?, ?, ?)
        """, (
            name,
            roll_number,
            registration_number
        ))


        connection.commit()


        return {
            "success": True,
            "message": "Student added successfully"
        }


    except sqlite3.IntegrityError:

        return {
            "success": False,
            "message": "Roll number already exists"
        }


    except Exception as error:

        return {
            "success": False,
            "message": f"Database error: {error}"
        }


    finally:

        connection.close()


# ============================================================
# GET STUDENT
# ============================================================

def get_student(
    roll_number
):

    create_database()

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            name,
            roll_number,
            registration_number,
            created_at
        FROM students
        WHERE roll_number = ?
    """, (
        str(roll_number).strip(),
    ))


    student = cursor.fetchone()

    connection.close()

    return student


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():

    create_database()

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            id,
            name,
            roll_number,
            registration_number,
            created_at
        FROM students
        ORDER BY id DESC
    """)


    students = cursor.fetchall()

    connection.close()

    return students


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance(
    roll_number
):

    create_database()

    roll_number = str(
        roll_number
    ).strip()


    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # CHECK STUDENT EXISTS
    # ========================================================

    cursor.execute("""
        SELECT name
        FROM students
        WHERE roll_number = ?
    """, (
        roll_number,
    ))


    student = cursor.fetchone()


    if not student:

        connection.close()

        return {
            "success": False,
            "message": "Student not found"
        }


    student_name = student[0]


    # ========================================================
    # CURRENT DATE AND TIME
    # ========================================================

    now = datetime.now()

    date = now.strftime(
        "%Y-%m-%d"
    )

    time = now.strftime(
        "%H:%M:%S"
    )


    # ========================================================
    # CHECK ALREADY MARKED
    # ========================================================

    cursor.execute("""
        SELECT id
        FROM attendance
        WHERE roll_number = ?
        AND date = ?
    """, (
        roll_number,
        date
    ))


    existing = cursor.fetchone()


    if existing:

        connection.close()

        return {
            "success": False,
            "message": "Attendance already marked today",
            "name": student_name,
            "roll_number": roll_number
        }


    # ========================================================
    # INSERT ATTENDANCE
    # ========================================================

    cursor.execute("""
        INSERT INTO attendance (
            roll_number,
            date,
            time,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        roll_number,
        date,
        time,
        "PRESENT"
    ))


    connection.commit()

    connection.close()


    return {
        "success": True,
        "message": "Attendance marked successfully",
        "name": student_name,
        "roll_number": roll_number,
        "time": time
    }


# ============================================================
# GET TODAY ATTENDANCE
# ============================================================

def get_today_attendance():

    create_database()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            a.roll_number,
            s.name,
            a.time,
            a.status
        FROM attendance AS a

        LEFT JOIN students AS s
        ON a.roll_number = s.roll_number

        WHERE a.date = ?

        ORDER BY a.time DESC
    """, (
        today,
    ))


    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# GET TOTAL STUDENTS
# ============================================================

def get_total_students():

    create_database()

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT COUNT(*)
        FROM students
    """)


    total = cursor.fetchone()[0]

    connection.close()

    return total


# ============================================================
# GET TODAY PRESENT COUNT
# ============================================================

def get_present_students():

    create_database()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE date = ?
        AND status = ?
    """, (
        today,
        "PRESENT"
    ))


    total = cursor.fetchone()[0]

    connection.close()

    return total


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    create_database()

    print()
    print("=" * 55)
    print("SMART ATTENDANCE AI - DATABASE READY")
    print("=" * 55)
    print()

    print(
        "Database Path:"
    )

    print(
        DATABASE_PATH
    )

    print()

    print(
        "Total Students:",
        get_total_students()
    )

    print(
        "Present Today:",
        get_present_students()
    )

    print()