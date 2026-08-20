import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "attendance.db"
)


# ============================================================
# DATABASE SETUP
# ============================================================

def create_database():

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            registration_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Attendance table
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


# Create database before dashboard starts
create_database()


# ============================================================
# GET TODAY'S ATTENDANCE
# ============================================================

def get_attendance():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cursor.execute("""
        SELECT
            a.roll_number,
            s.name,
            a.time,
            a.status
        FROM attendance a
        LEFT JOIN students s
        ON a.roll_number = s.roll_number
        WHERE a.date = ?
        ORDER BY a.time DESC
    """, (today,))

    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# GET TOTAL STUDENTS
# ============================================================

def get_total_students():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total


# ============================================================
# REFRESH DASHBOARD
# ============================================================

def refresh_dashboard():

    try:

        # Clear old rows
        for item in attendance_table.get_children():

            attendance_table.delete(
                item
            )

        # Get today's attendance
        records = get_attendance()

        # Add records to table
        for record in records:

            attendance_table.insert(
                "",
                tk.END,
                values=record
            )

        # Get statistics
        total_students = get_total_students()

        present_students = len(records)

        if total_students > 0:

            percentage = (
                present_students /
                total_students
            ) * 100

        else:

            percentage = 0

        # Update labels
        total_label.config(
            text=(
                "TOTAL STUDENTS\n"
                f"{total_students}"
            )
        )

        present_label.config(
            text=(
                "PRESENT TODAY\n"
                f"{present_students}"
            )
        )

        percentage_label.config(
            text=(
                "ATTENDANCE\n"
                f"{percentage:.1f}%"
            )
        )

    except Exception as error:

        print(
            "Dashboard error:",
            error
        )

    # Refresh every 3 seconds
    root.after(
        3000,
        refresh_dashboard
    )


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Smart Attendance AI"
)

root.geometry(
    "1000x650"
)

root.minsize(
    850,
    550
)

root.configure(
    bg="#07111f"
)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="SMART ATTENDANCE AI",
    font=("Arial", 28, "bold"),
    fg="#00ffcc",
    bg="#07111f"
)

title.pack(
    pady=(25, 5)
)


subtitle = tk.Label(
    root,
    text="LIVE ATTENDANCE DASHBOARD",
    font=("Arial", 12),
    fg="#8aa0b8",
    bg="#07111f"
)

subtitle.pack()


# ============================================================
# STATISTICS FRAME
# ============================================================

stats_frame = tk.Frame(
    root,
    bg="#07111f"
)

stats_frame.pack(
    pady=30
)


# ============================================================
# TOTAL STUDENTS
# ============================================================

total_label = tk.Label(
    stats_frame,
    text="TOTAL STUDENTS\n0",
    font=("Arial", 16, "bold"),
    fg="#ffffff",
    bg="#102338",
    width=22,
    height=4
)

total_label.grid(
    row=0,
    column=0,
    padx=10
)


# ============================================================
# PRESENT TODAY
# ============================================================

present_label = tk.Label(
    stats_frame,
    text="PRESENT TODAY\n0",
    font=("Arial", 16, "bold"),
    fg="#00ff88",
    bg="#102338",
    width=22,
    height=4
)

present_label.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# ATTENDANCE PERCENTAGE
# ============================================================

percentage_label = tk.Label(
    stats_frame,
    text="ATTENDANCE\n0%",
    font=("Arial", 16, "bold"),
    fg="#00ddff",
    bg="#102338",
    width=22,
    height=4
)

percentage_label.grid(
    row=0,
    column=2,
    padx=10
)


# ============================================================
# TABLE FRAME
# ============================================================

table_frame = tk.Frame(
    root,
    bg="#07111f"
)

table_frame.pack(
    padx=30,
    pady=(0, 25),
    fill="both",
    expand=True
)


# ============================================================
# TABLE
# ============================================================

columns = (
    "Roll Number",
    "Student Name",
    "Time",
    "Status"
)


attendance_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


# ============================================================
# TABLE HEADINGS
# ============================================================

for column in columns:

    attendance_table.heading(
        column,
        text=column
    )

    attendance_table.column(
        column,
        anchor="center",
        width=200
    )


attendance_table.pack(
    side="left",
    fill="both",
    expand=True
)


# ============================================================
# SCROLLBAR
# ============================================================

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=attendance_table.yview
)

attendance_table.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side="right",
    fill="y"
)


# ============================================================
# TABLE STYLE
# ============================================================

style = ttk.Style()

style.theme_use(
    "clam"
)

style.configure(
    "Treeview",
    background="#102338",
    foreground="white",
    fieldbackground="#102338",
    rowheight=35,
    font=("Arial", 11)
)

style.configure(
    "Treeview.Heading",
    background="#00aa99",
    foreground="white",
    font=("Arial", 11, "bold")
)

style.map(
    "Treeview",
    background=[
        ("selected", "#006f73")
    ],
    foreground=[
        ("selected", "white")
    ]
)


# ============================================================
# START DASHBOARD
# ============================================================

refresh_dashboard()

root.mainloop()