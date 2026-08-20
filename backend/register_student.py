import cv2
import os
import sys
import shutil
import time

import camera_state
from database import get_student


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FACE_DIR = os.path.join(
    BASE_DIR,
    "data",
    "faces"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

CASCADE_PATH = os.path.join(
    MODEL_DIR,
    "haarcascade_frontalface_default.xml"
)


# ============================================================
# SETTINGS
# ============================================================

IMAGE_COUNT = 40
IMAGE_SIZE = (200, 200)


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

os.makedirs(
    FACE_DIR,
    exist_ok=True
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# LOAD FACE DETECTOR
# ============================================================

def load_face_detector():

    if not os.path.exists(CASCADE_PATH):

        raise FileNotFoundError(
            f"Haar Cascade file not found:\n{CASCADE_PATH}"
        )

    detector = cv2.CascadeClassifier(
        CASCADE_PATH
    )

    if detector.empty():

        raise RuntimeError(
            "Could not load Haar Cascade file."
        )

    return detector


# ============================================================
# DELETE STUDENT FACE FOLDER
# ============================================================

def delete_face_folder(roll_number):

    student_folder = os.path.join(
        FACE_DIR,
        str(roll_number)
    )

    if os.path.exists(student_folder):

        shutil.rmtree(
            student_folder
        )


# ============================================================
# REGISTER FACE
# ============================================================

def register_student(
    roll_number,
    progress_callback=None
):

    roll_number = str(
        roll_number
    ).strip()


    # ========================================================
    # VALIDATION
    # ========================================================

    if not roll_number:

        return {
            "success": False,
            "message": "Roll number is required"
        }


    # ========================================================
    # CHECK STUDENT EXISTS
    # ========================================================

    student = get_student(
        roll_number
    )

    if not student:

        return {
            "success": False,
            "message": "Student not found. Add the student first."
        }


    student_id = student[0]
    student_name = student[1]


    # ========================================================
    # LOAD FACE DETECTOR
    # ========================================================

    try:

        detector = load_face_detector()

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }


    # ========================================================
    # CREATE STUDENT FOLDER
    # ========================================================

    student_folder = os.path.join(
        FACE_DIR,
        roll_number
    )


    # Remove old images if re-registering

    delete_face_folder(
        roll_number
    )

    os.makedirs(
        student_folder,
        exist_ok=True
    )


    # ========================================================
    # OPEN CAMERA
    # ========================================================

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )


    if not camera.isOpened():

        camera.release()

        return {
            "success": False,
            "message": "Could not open camera"
        }


    # ========================================================
    # START REGISTRATION
    # ========================================================

    count = 0
    cancelled = False


    print()
    print("=" * 60)
    print("SMART ATTENDANCE AI")
    print("FACE REGISTRATION")
    print("=" * 60)
    print()

    print("Student Name:", student_name)
    print("Roll Number:", roll_number)

    print()
    print("Look directly at the camera.")
    print("Slowly move your face slightly.")
    print("Press Q to cancel.")
    print()


    start_time = time.time()
    try:

        while count < IMAGE_COUNT:

            if time.time() - start_time > 15:
                print("Registration timed out after 15 seconds.")
                break

            success, frame = camera.read()


            if not success:

                continue


            # Mirror image

            frame = cv2.flip(
                frame,
                1
            )


            # Convert to grayscale

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )


            # Detect face

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )


            # =================================================
            # FACE DETECTED
            # =================================================

            if len(faces) > 0:


                # Select largest face

                x, y, w, h = max(
                    faces,
                    key=lambda face:
                    face[2] * face[3]
                )


                # Add padding

                padding = 20

                x1 = max(
                    0,
                    x - padding
                )

                y1 = max(
                    0,
                    y - padding
                )

                x2 = min(
                    frame.shape[1],
                    x + w + padding
                )

                y2 = min(
                    frame.shape[0],
                    y + h + padding
                )


                # Crop face

                face = gray[
                    y1:y2,
                    x1:x2
                ]


                # Resize face

                face = cv2.resize(
                    face,
                    IMAGE_SIZE
                )


                # Save image

                count += 1

                if progress_callback:
                    progress_callback(count, IMAGE_COUNT)

                filename = os.path.join(
                    student_folder,
                    f"{count:03d}.jpg"
                )


                cv2.imwrite(
                    filename,
                    face
                )


                # Draw face box

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


                # Show capture count near face

                text_y = max(
                    30,
                    y1 - 10
                )

                percent = int((count / IMAGE_COUNT) * 100)
                cv2.putText(
                    frame,
                    f"CAPTURING {percent}%",
                    (x1, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )


            else:

                cv2.putText(
                    frame,
                    "FACE NOT DETECTED",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )


            # =================================================
            # STATUS
            # =================================================

            cv2.putText(
                frame,
                f"Student: {student_name}",
                (20, frame.shape[0] - 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Roll: {roll_number}",
                (20, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 220),
                2
            )

            # Encode frame to JPEG and update shared state
            success_enc, jpeg = cv2.imencode('.jpg', frame)
            if success_enc:
                camera_state.latest_frame = jpeg.tobytes()

            # Check web cancel request
            if camera_state.cancel_requested:
                camera_state.cancel_requested = False
                cancelled = True
                break

            time.sleep(0.04)


    finally:

        camera.release()
        camera_state.latest_frame = None


    # ========================================================
    # CANCELLED
    # ========================================================

    if cancelled:

        delete_face_folder(
            roll_number
        )

        return {
            "success": False,
            "message": "Face registration cancelled",
            "images": count
        }


    # ========================================================
    # CHECK IMAGES
    # ========================================================

    if count < 5:

        delete_face_folder(
            roll_number
        )

        return {
            "success": False,
            "message": "Not enough face images captured",
            "images": count
        }


    # ========================================================
    # TRAIN MODEL
    # ========================================================

    print()
    print("=" * 60)
    print("FACE REGISTRATION COMPLETED")
    print(f"Images captured: {count}")
    print("=" * 60)
    print()

    print(
        "Training face recognition model..."
    )


    try:

        from train_model import train_model

        training_success = train_model()


    except Exception as error:

        return {
            "success": True,
            "message":
                f"Face registered but training failed: {error}",
            "name": student_name,
            "roll_number": roll_number,
            "images": count,
            "training": False
        }


    # ========================================================
    # SUCCESS
    # ========================================================

    if training_success:

        return {
            "success": True,
            "message":
                "Face registered and model trained successfully",
            "name": student_name,
            "roll_number": roll_number,
            "images": count,
            "training": True
        }


    return {
        "success": True,
        "message":
            "Face registered but model training failed",
        "name": student_name,
        "roll_number": roll_number,
        "images": count,
        "training": False
    }


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print()
        print("Usage:")
        print()

        print(
            "python backend/register_student.py ROLL_NUMBER"
        )

        print()

        sys.exit(1)


    roll_number = sys.argv[1]


    result = register_student(
        roll_number
    )


    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print()

    print(
        result
    )

    print()