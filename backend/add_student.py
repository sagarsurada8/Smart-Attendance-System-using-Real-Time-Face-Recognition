import sys
from database import add_student


# ============================================================
# ADD STUDENT
# ============================================================

def main():

    print()
    print("=" * 55)
    print("SMART ATTENDANCE AI - ADD STUDENT")
    print("=" * 55)
    print()


    # --------------------------------------------------------
    # COMMAND LINE MODE
    # --------------------------------------------------------

    if len(sys.argv) >= 3:

        name = sys.argv[1].strip()
        roll_number = sys.argv[2].strip()

        if len(sys.argv) >= 4:

            registration_number = sys.argv[3].strip()

        else:

            registration_number = ""


    # --------------------------------------------------------
    # MANUAL INPUT MODE
    # --------------------------------------------------------

    else:

        name = input(
            "Enter student name: "
        ).strip()

        roll_number = input(
            "Enter roll number: "
        ).strip()

        registration_number = input(
            "Enter registration number (optional): "
        ).strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        print()
        print("ERROR: Student name is required.")
        print()

        return


    if not roll_number:

        print()
        print("ERROR: Roll number is required.")
        print()

        return


    # --------------------------------------------------------
    # ADD STUDENT
    # --------------------------------------------------------

    result = add_student(
        roll_number=roll_number,
        name=name,
        registration_number=registration_number
    )


    print()
    print("=" * 55)


    if result["success"]:

        print("STUDENT ADDED SUCCESSFULLY")

        print()

        print(
            "Name:",
            name
        )

        print(
            "Roll Number:",
            roll_number
        )

        if registration_number:

            print(
                "Registration Number:",
                registration_number
            )


    else:

        print("FAILED TO ADD STUDENT")

        print()

        print(
            "Reason:",
            result["message"]
        )


    print("=" * 55)
    print()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()