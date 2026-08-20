import cv2
import numpy as np
import os
import sqlite3
import time

import camera_state

from database import create_database, mark_attendance


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "face_model.yml"
)

LABELS_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "labels.npy"
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "attendance.db"
)

# Lower = stricter recognition
# 120 is your current value.
RECOGNITION_THRESHOLD = 100

# Number of matching frames required
REQUIRED_MATCHES = 3

# Maximum scanning time
SCAN_TIMEOUT = 12

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


# ============================================================
# DATABASE
# ============================================================

create_database()


def get_student_name(roll_number):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM students
        WHERE roll_number = ?
        """,
        (str(roll_number),)
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return f"Student {roll_number}"


# ============================================================
# CHECK MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        "\nFace model not found.\n"
        "Run:\n"
        "python backend\\train_model.py\n"
    )


if not os.path.exists(LABELS_PATH):

    raise FileNotFoundError(
        "\nLabels file not found.\n"
        "Run:\n"
        "python backend\\train_model.py\n"
    )


# ============================================================
# LBPH RECOGNIZER
# ============================================================

try:

    recognizer = cv2.face.LBPHFaceRecognizer_create()

except AttributeError:

    raise RuntimeError(
        "\ncv2.face is not available.\n\n"
        "Run:\n"
        "python -m pip uninstall opencv-python -y\n"
        "python -m pip install opencv-contrib-python\n"
    )


if os.path.exists(MODEL_PATH):
    recognizer.read(MODEL_PATH)


# ============================================================
# LOAD LABELS
# ============================================================

labels = {}
if os.path.exists(LABELS_PATH):
    labels = np.load(
        LABELS_PATH,
        allow_pickle=True
    ).item()

print("Initial loaded labels:")
print(labels)


# ============================================================
# FACE DETECTOR
# ============================================================

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "haarcascade_frontalface_default.xml"
)

face_detector = cv2.CascadeClassifier(
    CASCADE_PATH
)


if face_detector.empty():

    raise RuntimeError(
        "Haar Cascade face detector could not be loaded."
    )


# ============================================================
# DRAW TEXT WITH BACKGROUND
# ============================================================

def draw_text_box(
    frame,
    text,
    x,
    y,
    color,
    font_scale=0.55,
    thickness=1
):

    font = cv2.FONT_HERSHEY_SIMPLEX

    (
        text_width,
        text_height
    ), baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness
    )

    # Keep text inside screen
    y = max(
        text_height + 10,
        y
    )

    # Background
    cv2.rectangle(
        frame,
        (
            x - 5,
            y - text_height - 8
        ),
        (
            x + text_width + 8,
            y + baseline + 5
        ),
        (0, 0, 0),
        -1
    )

    # Text
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA
    )


# ============================================================
# RECOGNITION FUNCTION
# ============================================================

def recognize_once(timeout=SCAN_TIMEOUT):

    print()
    print("=" * 60)
    print("SMART ATTENDANCE AI")
    print("FAST FACE SCANNING")
    print("=" * 60)

    # --------------------------------------------------------
    # RELOAD MODEL AND LABELS FROM DISK
    # --------------------------------------------------------
    global recognizer, labels
    try:
        if os.path.exists(MODEL_PATH):
            recognizer.read(MODEL_PATH)
        if os.path.exists(LABELS_PATH):
            labels = np.load(
                LABELS_PATH,
                allow_pickle=True
            ).item()
        print("Model and labels reloaded successfully:")
        print(labels)
    except Exception as e:
        print(f"Error reloading model/labels: {e}")

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    if not camera.isOpened():

        return {
            "recognized": False,
            "error": "Could not open camera"
        }


    start_time = time.time()

    consecutive_matches = 0

    last_roll = None
    last_name = None
    last_score = 0

    result = None


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    try:

        while True:

            success, frame = camera.read()

            if not success:

                continue


            # Mirror camera
            frame = cv2.flip(
                frame,
                1
            )


            # ------------------------------------------------
            # GRAYSCALE
            # ------------------------------------------------

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )


            # ------------------------------------------------
            # FACE DETECTION
            # ------------------------------------------------

            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.15,
                minNeighbors=5,
                minSize=(90, 90)
            )


            # ------------------------------------------------
            # TOP HEADER
            # ------------------------------------------------

            cv2.putText(
                frame,
                "SMART ATTENDANCE AI",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 220),
                2,
                cv2.LINE_AA
            )


            cv2.putText(
                frame,
                "LOOK AT THE CAMERA",
                (20, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 220),
                1,
                cv2.LINE_AA
            )


            # =================================================
            # NO FACE
            # =================================================

            if len(faces) == 0:

                consecutive_matches = 0

                cv2.putText(
                    frame,
                    "SEARCHING FOR FACE...",
                    (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 220),
                    1,
                    cv2.LINE_AA
                )


            # =================================================
            # PROCESS FACE
            # =================================================

            for (
                x,
                y,
                w,
                h
            ) in faces:

                face = gray[
                    y:y + h,
                    x:x + w
                ]


                # Resize exactly like training
                face = cv2.resize(
                    face,
                    (200, 200)
                )


                # ------------------------------------------------
                # PREDICT
                # ------------------------------------------------

                label, distance = recognizer.predict(
                    face
                )


                print(
                    f"Label: {label} | "
                    f"Distance: {distance:.2f}"
                )


                # ------------------------------------------------
                # RECOGNIZED
                # ------------------------------------------------

                if (
                    distance < RECOGNITION_THRESHOLD
                    and label in labels
                ):

                    roll_number = str(
                        labels[label]
                    )

                    student_name = get_student_name(
                        roll_number
                    )


                    # Convert LBPH distance to display score
                    score = max(
                        0,
                        min(
                            100,
                            100 - distance
                        )
                    )


                    # Check consecutive match
                    if last_roll == roll_number:

                        consecutive_matches += 1

                    else:

                        consecutive_matches = 1

                        last_roll = roll_number

                        last_name = student_name

                        last_score = score


                    # ------------------------------------------------
                    # GREEN FACE BOX
                    # ------------------------------------------------

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 120),
                        2
                    )


                    # ------------------------------------------------
                    # SCANNING LINE
                    # ------------------------------------------------

                    scan_y = (
                        y +
                        int(
                            (time.time() * 250)
                            % max(h, 1)
                        )
                    )

                    cv2.line(
                        frame,
                        (x, scan_y),
                        (x + w, scan_y),
                        (0, 255, 255),
                        2
                    )


                    # ------------------------------------------------
                    # RESULT BESIDE FACE
                    # ------------------------------------------------

                    result_x = x + w + 15

                    # If there isn't enough space on right,
                    # show it on left.
                    if result_x + 220 > frame.shape[1]:

                        result_x = x - 220

                    result_x = max(
                        10,
                        result_x
                    )


                    result_y = y + 25


                    draw_text_box(
                        frame,
                        "IDENTITY VERIFIED",
                        result_x,
                        result_y,
                        (0, 255, 120),
                        0.48,
                        1
                    )


                    draw_text_box(
                        frame,
                        student_name,
                        result_x,
                        result_y + 28,
                        (255, 255, 255),
                        0.55,
                        1
                    )


                    draw_text_box(
                        frame,
                        f"ROLL: {roll_number}",
                        result_x,
                        result_y + 56,
                        (0, 255, 220),
                        0.48,
                        1
                    )


                    draw_text_box(
                        frame,
                        f"MATCH: {score:.1f}%",
                        result_x,
                        result_y + 84,
                        (0, 255, 220),
                        0.48,
                        1
                    )


                    # ------------------------------------------------
                    # SCANNING STATUS
                    # ------------------------------------------------

                    if consecutive_matches < REQUIRED_MATCHES:

                        draw_text_box(
                            frame,
                            "VERIFYING...",
                            result_x,
                            result_y + 112,
                            (0, 255, 255),
                            0.48,
                            1
                        )


                    # ------------------------------------------------
                    # CONFIRMED
                    # ------------------------------------------------

                    if (
                        consecutive_matches
                        >= REQUIRED_MATCHES
                    ):

                        attendance_marked = mark_attendance(
                            roll_number
                        )


                        if attendance_marked:

                            attendance_message = (
                                "ATTENDANCE MARKED"
                            )

                        else:

                            attendance_message = (
                                "ALREADY MARKED TODAY"
                            )


                        # Show attendance result
                        draw_text_box(
                            frame,
                            attendance_message,
                            result_x,
                            result_y + 112,
                            (0, 255, 120),
                            0.48,
                            1
                        )


                        # ------------------------------------------------
                        # FINAL LARGE MESSAGE
                        # ------------------------------------------------

                        center_x = 20
                        center_y = frame.shape[0] - 55

                        cv2.putText(
                            frame,
                            attendance_message,
                            (
                                center_x,
                                center_y
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            (0, 255, 120),
                            2,
                            cv2.LINE_AA
                        )


                        # Update shared state with final frame
                        success_enc, jpeg = cv2.imencode('.jpg', frame)
                        if success_enc:
                            camera_state.latest_frame = jpeg.tobytes()

                        # Keep result visible briefly
                        time.sleep(1.0)


                        result = {
                            "recognized": True,
                            "name": student_name,
                            "roll_number": roll_number,
                            "match": round(
                                score,
                                1
                            ),
                            "attendance": attendance_message
                        }


                        return result


                # =================================================
                # UNKNOWN FACE
                # =================================================

                else:

                    consecutive_matches = 0

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 0, 255),
                        2
                    )


                    result_x = x + w + 15

                    if result_x + 200 > frame.shape[1]:

                        result_x = x - 200

                    result_x = max(
                        10,
                        result_x
                    )


                    draw_text_box(
                        frame,
                        "UNKNOWN FACE",
                        result_x,
                        y + 25,
                        (0, 0, 255),
                        0.55,
                        1
                    )


                    draw_text_box(
                        frame,
                        "PLEASE TRY AGAIN",
                        result_x,
                        y + 55,
                        (0, 180, 255),
                        0.45,
                        1
                    )


            # ====================================================
            # TIMEOUT
            # ====================================================

            if (
                time.time() - start_time
                > timeout
            ):

                return {
                    "recognized": False,
                    "message": "Face recognition timed out"
                }


            # Encode frame to JPEG and update shared state
            success_enc, jpeg = cv2.imencode('.jpg', frame)
            if success_enc:
                camera_state.latest_frame = jpeg.tobytes()

            # Check web cancel request
            if camera_state.cancel_requested:
                camera_state.cancel_requested = False
                return {
                    "recognized": False,
                    "message": "Recognition cancelled"
                }

            time.sleep(0.04)


    finally:

        camera.release()
        camera_state.latest_frame = None


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    result = recognize_once()

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)