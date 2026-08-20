import cv2
import os
import sys


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# HAAR CASCADE PATH
# ============================================================

cascade_path = os.path.join(
    BASE_DIR,
    "models",
    "haarcascade_frontalface_default.xml"
)


print("Loading face detector:")
print(cascade_path)


# ============================================================
# CHECK CASCADE FILE
# ============================================================

if not os.path.exists(cascade_path):

    print()
    print("ERROR: Haar Cascade file not found.")
    print()
    print("Expected:")
    print(cascade_path)
    print()

    sys.exit(1)


# ============================================================
# LOAD FACE DETECTOR
# ============================================================

face_cascade = cv2.CascadeClassifier(
    cascade_path
)


if face_cascade.empty():

    print()
    print("ERROR: Could not load Haar Cascade.")
    print("Cascade path:")
    print(cascade_path)
    print()

    sys.exit(1)


print("Face detector loaded successfully.")


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Could not open camera.")

    sys.exit(1)


print("Face detection started.")
print("Press Q to close.")


# ============================================================
# FACE DETECTION LOOP
# ============================================================

while True:

    success, frame = camera.read()


    if not success:

        print(
            "ERROR: Could not read camera frame"
        )

        break


    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )


    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # Detect faces
    faces = face_cascade.detectMultiScale(

        gray,

        scaleFactor=1.1,

        minNeighbors=5,

        minSize=(80, 80)

    )


    # ========================================================
    # DRAW FACE BOXES
    # ========================================================

    for (x, y, w, h) in faces:

        cv2.rectangle(

            frame,

            (x, y),

            (x + w, y + h),

            (0, 255, 0),

            2

        )


        cv2.putText(

            frame,

            "FACE DETECTED",

            (x, y - 10),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2

        )


    # ========================================================
    # FACE COUNT
    # ========================================================

    cv2.putText(

        frame,

        f"Faces: {len(faces)}",

        (20, 40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0, 255, 0),

        2

    )


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(

        "Smart Attendance - Face Detection",

        frame

    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()
