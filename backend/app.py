
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
import os
import time
import numpy as np
import cv2

import camera_state
from database import create_database, add_student, get_student
from recognize import recognize_once
from register_student import register_student


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# DATABASE
# ============================================================

create_database()

DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "attendance.db"
)


# ============================================================
# PROGRESS TRACKING
# ============================================================

registration_progress = {}


# ============================================================
# VIDEO FEED AND CANCEL
# ============================================================

# Pre-generate a cyberpunk placeholder frame
placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(placeholder_img, "3D BIOMETRIC CAMERA STANDBY", (80, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (225, 255, 0), 2, cv2.LINE_AA)
_, placeholder_jpeg = cv2.imencode('.jpg', placeholder_img)
PLACEHOLDER_BYTES = placeholder_jpeg.tobytes()

@app.route("/api/video_feed")
def video_feed():
    def gen_frames():
        while True:
            # Yield latest camera frame if available, else placeholder
            frame = camera_state.latest_frame
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + PLACEHOLDER_BYTES + b'\r\n')
            time.sleep(0.04) # Limit stream to ~25 FPS

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/api/camera/cancel", methods=["POST"])
def cancel_camera():
    camera_state.cancel_requested = True
    return jsonify({
        "success": True,
        "message": "Cancel request sent to camera thread"
    })


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "status": "online",
        "message": "Smart Attendance AI backend is running"
    })


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def status():

    return jsonify({
        "success": True,
        "system": "online",
        "camera": "ready",
        "recognition": "ready"
    })


# ============================================================
# TAKE ATTENDANCE / FACE RECOGNITION
# ============================================================

@app.route("/api/recognition", methods=["GET"])
def recognition():

    try:

        print()
        print("=" * 60)
        print("FACE RECOGNITION REQUEST")
        print("=" * 60)
        print("Starting camera...")
        print()

        result = recognize_once(
            timeout=15
        )

        if result is None:

            return jsonify({
                "success": False,
                "recognized": False,
                "message": "No result received"
            }), 500


        # ----------------------------------------------------
        # RECOGNIZED
        # ----------------------------------------------------

        if result.get("recognized"):

            return jsonify({

                "success": True,

                "recognized": True,

                "name": result.get(
                    "name",
                    ""
                ),

                "roll_number": result.get(
                    "roll_number",
                    ""
                ),

                "match": result.get(
                    "match",
                    0
                ),

                "attendance": result.get(
                    "attendance",
                    ""
                ),

                "message": "Face recognized successfully"

            })


        # ----------------------------------------------------
        # NOT RECOGNIZED
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "recognized": False,

            "message": result.get(
                "message",
                "Face not recognized"
            )

        })


    except Exception as error:

        print()
        print("=" * 60)
        print("RECOGNITION ERROR")
        print("=" * 60)
        print(error)
        print()

        return jsonify({

            "success": False,

            "recognized": False,

            "message": str(error)

        }), 500


# ============================================================
# ADD STUDENT
# ============================================================

@app.route("/api/register", methods=["POST"])
def register():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No student information received"

            }), 400


        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()


        roll_number = str(
            data.get(
                "roll_number",
                ""
            )
        ).strip()


        registration_number = str(
            data.get(
                "registration_number",
                ""
            )
        ).strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:

            return jsonify({

                "success": False,

                "message":
                    "Student name is required"

            }), 400


        if not roll_number:

            return jsonify({

                "success": False,

                "message":
                    "Roll number is required"

            }), 400


        if not registration_number:

            return jsonify({

                "success": False,

                "message":
                    "Registration number is required"

            }), 400


        # ----------------------------------------------------
        # PRINT
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("NEW STUDENT REGISTRATION")
        print("=" * 60)
        print("Name       :", name)
        print("Roll Number:", roll_number)
        print("Registration:", registration_number)
        print("=" * 60)
        print()


        # ----------------------------------------------------
        # REGISTER
        # ----------------------------------------------------

        # Check if student already exists
        student_exists = get_student(roll_number) is not None

        if not student_exists:
            add_result = add_student(
                roll_number=roll_number,
                name=name,
                registration_number=registration_number
            )
            if not add_result.get("success"):
                return jsonify(add_result), 400

        # Define progress callback
        registration_progress[roll_number] = 0
        def progress_cb(current, total):
            registration_progress[roll_number] = int((current / total) * 100)

        # Run face registration
        try:
            result = register_student(
                roll_number=roll_number,
                progress_callback=progress_cb
            )
        finally:
            registration_progress.pop(roll_number, None)

        if result is None:
            # Clean up if just created
            if not student_exists:
                try:
                    connection = sqlite3.connect(DATABASE_PATH)
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM students WHERE roll_number = ?", (roll_number,))
                    connection.commit()
                    connection.close()
                except Exception:
                    pass

            return jsonify({
                "success": False,
                "message": "Registration returned no result"
            }), 500

        # Clean up database if registration failed and student didn't exist before
        if not result.get("success") and not student_exists:
            try:
                connection = sqlite3.connect(DATABASE_PATH)
                cursor = connection.cursor()
                cursor.execute("DELETE FROM students WHERE roll_number = ?", (roll_number,))
                connection.commit()
                connection.close()
            except Exception:
                pass

        return jsonify(result)


    except Exception as error:

        print()
        print("=" * 60)
        print("REGISTRATION ERROR")
        print("=" * 60)
        print(error)
        print()

        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


# ============================================================
# GET REGISTER PROGRESS
# ============================================================

@app.route("/api/register/progress/<roll_number>", methods=["GET"])
def register_progress(roll_number):

    progress = registration_progress.get(roll_number, 0)

    return jsonify({
        "success": True,
        "progress": progress
    })


# ============================================================
# GET ALL STUDENTS
# ============================================================

@app.route("/api/students", methods=["GET"])
def get_students():

    connection = None

    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

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

        rows = cursor.fetchall()


        students = []


        for row in rows:

            students.append({

                "id": row[0],

                "name": row[1],

                "roll_number": row[2],

                "registration_number": row[3],

                "created_at": row[4]

            })


        return jsonify({

            "success": True,

            "students": students

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


    finally:

        if connection:

            connection.close()


# ============================================================
# TODAY'S ATTENDANCE
# ============================================================

@app.route("/api/attendance", methods=["GET"])
def get_attendance():

    connection = None

    try:

        from datetime import datetime

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )


        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()


        cursor.execute("""
            SELECT
                a.id,
                a.roll_number,
                s.name,
                a.date,
                a.time,
                a.status
            FROM attendance a
            LEFT JOIN students s
            ON a.roll_number = s.roll_number
            WHERE a.date = ?
            ORDER BY a.time DESC
        """, (today,))


        rows = cursor.fetchall()


        attendance = []


        for row in rows:

            attendance.append({

                "id": row[0],

                "roll_number": row[1],

                "name": row[2] or "Unknown",

                "date": row[3],

                "time": row[4],

                "status": row[5]

            })


        return jsonify({

            "success": True,

            "date": today,

            "attendance": attendance

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


    finally:

        if connection:

            connection.close()


# ============================================================
# ATTENDANCE STATISTICS
# ============================================================

@app.route("/api/attendance/stats", methods=["GET"])
def attendance_stats():

    connection = None

    try:

        from datetime import datetime

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )


        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()


        # Total students

        cursor.execute("""
            SELECT COUNT(*)
            FROM students
        """)

        total_students = cursor.fetchone()[0]


        # Present today

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
        """, (today,))


        present_today = cursor.fetchone()[0]


        # Percentage

        if total_students > 0:

            percentage = (
                present_today /
                total_students
            ) * 100

        else:

            percentage = 0


        return jsonify({

            "success": True,

            "total_students":
                total_students,

            "present_today":
                present_today,

            "attendance_percentage":
                round(
                    percentage,
                    1
                )

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


    finally:

        if connection:

            connection.close()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("          SMART ATTENDANCE AI")
    print("             FLASK BACKEND")
    print("=" * 60)
    print()
    print("Backend running at:")
    print("http://127.0.0.1:5000")
    print()
    print("Available APIs:")
    print("GET  /")
    print("GET  /api/status")
    print("GET  /api/recognition")
    print("POST /api/register")
    print("GET  /api/students")
    print("GET  /api/attendance")
    print("GET  /api/attendance/stats")
    print()
    print("=" * 60)
    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False

    )

