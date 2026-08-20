import cv2
import os
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "faces"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "face_model.yml"
)

LABEL_PATH = os.path.join(
    MODEL_DIR,
    "labels.npy"
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    DATA_PATH,
    exist_ok=True
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# CHECK OPENCV LBPH
# ============================================================

def create_recognizer():

    try:

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        return recognizer

    except AttributeError:

        raise RuntimeError(
            "\nOpenCV Face module is not available.\n\n"
            "Run these commands inside your virtual environment:\n\n"
            "python -m pip uninstall opencv-python -y\n"
            "python -m pip install opencv-contrib-python\n\n"
            "Then run train_model.py again."
        )


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    print()
    print("=" * 60)
    print("SMART ATTENDANCE AI")
    print("FACE MODEL TRAINING")
    print("=" * 60)
    print()


    # ========================================================
    # CREATE RECOGNIZER
    # ========================================================

    try:

        recognizer = create_recognizer()

    except Exception as error:

        print(error)

        return False


    # ========================================================
    # DATA
    # ========================================================

    faces = []

    labels = []

    label_map = {}

    current_label = 0


    # ========================================================
    # CHECK FACE DIRECTORY
    # ========================================================

    if not os.path.exists(DATA_PATH):

        print(
            "ERROR: Face data folder does not exist."
        )

        print(
            f"Expected:\n{DATA_PATH}"
        )

        return False


    # ========================================================
    # FIND STUDENT FOLDERS
    # ========================================================

    student_folders = sorted(
        os.listdir(DATA_PATH)
    )


    if len(student_folders) == 0:

        print(
            "ERROR: No student face folders found."
        )

        print(
            f"Expected folders inside:\n{DATA_PATH}"
        )

        return False


    # ========================================================
    # LOAD STUDENT IMAGES
    # ========================================================

    for roll_number in student_folders:

        student_folder = os.path.join(
            DATA_PATH,
            roll_number
        )


        # Ignore files
        if not os.path.isdir(
            student_folder
        ):

            continue


        print(
            f"Loading student: {roll_number}"
        )


        # Map numeric LBPH label to roll number
        label_map[
            current_label
        ] = str(roll_number)


        image_files = sorted(
            os.listdir(
                student_folder
            )
        )


        student_image_count = 0


        # ====================================================
        # LOAD IMAGES
        # ====================================================

        for filename in image_files:

            image_path = os.path.join(
                student_folder,
                filename
            )


            # Only process image files
            if not filename.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".bmp"
                )
            ):

                continue


            image = cv2.imread(
                image_path,
                cv2.IMREAD_GRAYSCALE
            )


            if image is None:

                print(
                    f"  WARNING: Could not read {filename}"
                )

                continue


            # Resize to the same size
            image = cv2.resize(
                image,
                (200, 200)
            )


            faces.append(
                image
            )

            labels.append(
                current_label
            )


            student_image_count += 1


        print(
            f"  Images loaded: {student_image_count}"
        )


        # Only move to next label if
        # this student has images
        if student_image_count > 0:

            current_label += 1

        else:

            # Remove empty student from label map
            del label_map[
                current_label
            ]


    # ========================================================
    # CHECK TRAINING DATA
    # ========================================================

    print()


    if len(faces) == 0:

        print(
            "ERROR: No valid face images found."
        )

        print(
            f"Check:\n{DATA_PATH}"
        )

        return False


    if len(label_map) == 0:

        print(
            "ERROR: No students available for training."
        )

        return False


    # ========================================================
    # SHOW TRAINING INFORMATION
    # ========================================================

    print(
        f"Students : {len(label_map)}"
    )

    print(
        f"Images   : {len(faces)}"
    )

    print()


    # ========================================================
    # TRAIN
    # ========================================================

    print(
        "Training LBPH face recognition model..."
    )

    print()


    try:

        recognizer.train(
            faces,
            np.array(
                labels,
                dtype=np.int32
            )
        )

    except Exception as error:

        print()
        print(
            "TRAINING ERROR:"
        )

        print(error)

        return False


    # ========================================================
    # SAVE MODEL
    # ========================================================

    try:

        recognizer.save(
            MODEL_PATH
        )

        np.save(
            LABEL_PATH,
            label_map
        )

    except Exception as error:

        print()
        print(
            "MODEL SAVE ERROR:"
        )

        print(error)

        return False


    # ========================================================
    # VERIFY FILES
    # ========================================================

    if not os.path.exists(
        MODEL_PATH
    ):

        print(
            "ERROR: face_model.yml was not created."
        )

        return False


    if not os.path.exists(
        LABEL_PATH
    ):

        print(
            "ERROR: labels.npy was not created."
        )

        return False


    # ========================================================
    # SUCCESS
    # ========================================================

    print()
    print("=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Students : {len(label_map)}"
    )

    print(
        f"Images   : {len(faces)}"
    )

    print()
    print(
        f"Model:"
    )

    print(
        MODEL_PATH
    )

    print()
    print(
        f"Labels:"
    )

    print(
        LABEL_PATH
    )

    print("=" * 60)
    print()


    return True


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    success = train_model()

    if success:

        print(
            "Model is ready for recognition."
        )

    else:

        print(
            "Model training failed."
        )
