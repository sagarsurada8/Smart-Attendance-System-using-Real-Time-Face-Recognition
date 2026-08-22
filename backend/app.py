
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
import os
import time
import numpy as np
import cv2

import base64
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
# BASE64 IMAGE DECODER
# ============================================================

def decode_base64_image(base64_str):
    try:
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None


# ============================================================
# REGISTER STUDENT FRAME BY FRAME (WebRTC)
# ============================================================

FACE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "faces"
)

@app.route("/api/register_frame", methods=["POST"])
def register_frame():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "message": "No student information received"}), 400

        name = str(data.get("name", "")).strip()
        roll_number = str(data.get("roll_number", "")).strip()
        registration_number = str(data.get("registration_number", "")).strip()
        image_base64 = data.get("image", "")
        frame_index = int(data.get("frame_index", 0))
        total_frames = int(data.get("total_frames", 40))

        if not name:
            return jsonify({"success": False, "message": "Student name is required"}), 400
        if not roll_number:
            return jsonify({"success": False, "message": "Roll number is required"}), 400
        if not image_base64:
            return jsonify({"success": False, "message": "Image frame data is required"}), 400

        # Add student to database on first frame
        if frame_index == 0:
            student_exists = get_student(roll_number) is not None
            if not student_exists:
                add_result = add_student(
                    roll_number=roll_number,
                    name=name,
                    registration_number=registration_number
                )
                if not add_result.get("success"):
                    return jsonify(add_result), 400

        # Decode image
        frame = decode_base64_image(image_base64)
        if frame is None:
            return jsonify({"success": False, "message": "Failed to process image frame"}), 400

        # Detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "haarcascade_frontalface_default.xml")
        detector = cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        if len(faces) == 0:
            return jsonify({"success": False, "message": "Face not detected. Look straight at the camera."}), 200

        # Select largest face
        x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(frame.shape[1], x + w + padding)
        y2 = min(frame.shape[0], y + h + padding)

        face_crop = gray[y1:y2, x1:x2]
        face_crop = cv2.equalizeHist(face_crop)
        face_resize = cv2.resize(face_crop, (200, 200))

        # Save cropped face
        student_folder = os.path.join(FACE_DIR, roll_number)
        
        # Clean folder on first frame
        if frame_index == 0:
            import shutil
            if os.path.exists(student_folder):
                shutil.rmtree(student_folder)
        
        os.makedirs(student_folder, exist_ok=True)
        filename = os.path.join(student_folder, f"{frame_index + 1:03d}.jpg")
        cv2.imwrite(filename, face_resize)

        # Train model if this is the last frame
        training = False
        if frame_index == total_frames - 1:
            from train_model import train_model
            try:
                training = train_model()
            except Exception as e:
                print(f"Training error: {e}")

        return jsonify({
            "success": True,
            "message": f"Frame {frame_index + 1}/{total_frames} captured",
            "name": name,
            "roll_number": roll_number,
            "images": frame_index + 1,
            "training": training
        })

    except Exception as error:
        print(f"Register frame error: {error}")
        return jsonify({"success": False, "message": str(error)}), 500


# ============================================================
# RECOGNIZE FACE FRAME BY FRAME (WebRTC)
# ============================================================

recognition_sessions = {}

@app.route("/api/recognize_frame", methods=["POST"])
def recognize_frame():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("image"):
            return jsonify({"success": False, "message": "No image frame received"}), 400

        image_base64 = data.get("image")
        frame = decode_base64_image(image_base64)
        if frame is None:
            return jsonify({"success": False, "message": "Failed to decode image frame"}), 400

        # Grayscale and detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "haarcascade_frontalface_default.xml")
        detector = cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(90, 90))

        if len(faces) == 0:
            return jsonify({
                "success": True,
                "detected": False,
                "message": "Searching for face..."
            })

        # Load LBPH model & labels
        from recognize import MODEL_PATH, LABELS_PATH, RECOGNITION_THRESHOLD, REQUIRED_MATCHES, get_student_name
        import recognize
        
        # Reload model if updated
        if os.path.exists(MODEL_PATH):
            recognize.recognizer.read(MODEL_PATH)
        if os.path.exists(LABELS_PATH):
            recognize.labels = np.load(LABELS_PATH, allow_pickle=True).item()

        # Process largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(frame.shape[1], x + w + padding)
        y2 = min(frame.shape[0], y + h + padding)

        face_crop = gray[y1:y2, x1:x2]
        face_crop = cv2.equalizeHist(face_crop)
        face_resize = cv2.resize(face_crop, (200, 200))

        label, distance = recognize.recognizer.predict(face_resize)
        
        recognized = False
        student_name = "Unknown"
        roll_number = ""
        score = 0
        attendance_message = "Verifying..."

        if distance < RECOGNITION_THRESHOLD and label in recognize.labels:
            roll_number = str(recognize.labels[label])
            student_name = get_student_name(roll_number)
            score = max(0, min(100, 100 - distance))
            recognized = True

            # Track matches per roll number for this client (robust accumulator)
            client_ip = request.remote_addr
            now = time.time()
            
            if client_ip not in recognition_sessions:
                recognition_sessions[client_ip] = {"last_time": now, "counts": {}}
                
            session = recognition_sessions[client_ip]
            
            # Reset session if inactive for > 8 seconds
            if now - session.get("last_time", 0) > 8.0:
                session["counts"] = {}
                
            session["last_time"] = now
            counts = session["counts"]
            
            # Increment count for this roll number
            counts[roll_number] = counts.get(roll_number, 0) + 1
            matches = counts[roll_number]

            # If matches met, mark attendance
            if matches >= REQUIRED_MATCHES:
                from database import mark_attendance
                res = mark_attendance(roll_number)
                if res.get("success"):
                    attendance_message = "ATTENDANCE MARKED"
                else:
                    attendance_message = "ALREADY MARKED TODAY"

                recognition_sessions.pop(client_ip, None)

                return jsonify({
                    "success": True,
                    "detected": True,
                    "recognized": True,
                    "confirmed": True,
                    "name": student_name,
                    "roll_number": roll_number,
                    "match": round(score, 1),
                    "attendance": attendance_message,
                    "box": [int(x), int(y), int(w), int(h)]
                })

        return jsonify({
            "success": True,
            "detected": True,
            "recognized": recognized,
            "confirmed": False,
            "name": student_name,
            "roll_number": roll_number,
            "match": round(score, 1),
            "attendance": attendance_message,
            "box": [int(x), int(y), int(w), int(h)]
        })

    except Exception as e:
        print(f"Recognize frame error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


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
    print("POST /api/recognize_frame")
    print("POST /api/register_frame")
    print("GET  /api/students")
    print("GET  /api/attendance")
    print("GET  /api/attendance/stats")
    print()
    print("=" * 60)
    print()


    port = int(os.environ.get("PORT", 5000))
    app.run(

        host="0.0.0.0",

        port=port,

        debug=False

    )

