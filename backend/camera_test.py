import cv2
import sys


# ============================================================
# CAMERA TEST
# ============================================================

print()
print("=" * 50)
print("       SMART ATTENDANCE AI")
print("          CAMERA TEST")
print("=" * 50)
print()


# ============================================================
# OPEN CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

# Windows camera backend
if not camera.isOpened():

    camera.release()

    print("ERROR: Could not open camera.")
    print()
    print("Check that:")
    print("1. Your webcam is connected.")
    print("2. No other application is using the camera.")
    print("3. Camera permission is enabled.")
    print()

    sys.exit(1)


# ============================================================
# CAMERA SETTINGS
# ============================================================

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


print("Camera started successfully.")
print("Camera resolution: 640 x 480")
print("Press Q to close.")
print()


# ============================================================
# CAMERA LOOP
# ============================================================

try:

    while True:

        success, frame = camera.read()


        # ----------------------------------------------------
        # CHECK FRAME
        # ----------------------------------------------------

        if not success:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        # ----------------------------------------------------
        # MIRROR CAMERA
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        # ----------------------------------------------------
        # DISPLAY TEXT
        # ----------------------------------------------------

        cv2.putText(

            frame,

            "SMART ATTENDANCE AI",

            (20, 35),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 255, 220),

            2

        )


        cv2.putText(

            frame,

            "CAMERA READY",

            (20, 70),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            (0, 255, 0),

            2

        )


        cv2.putText(

            frame,

            "Press Q to close",

            (20, 105),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.5,

            (255, 255, 255),

            1

        )


        # ----------------------------------------------------
        # SHOW CAMERA
        # ----------------------------------------------------

        cv2.imshow(

            "Smart Attendance - Camera Test",

            frame

        )


        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break


except KeyboardInterrupt:

    print()
    print("Camera test stopped.")


finally:

    # ========================================================
    # RELEASE CAMERA
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()

    print()
    print("Camera released.")
    print("Camera test finished.")
