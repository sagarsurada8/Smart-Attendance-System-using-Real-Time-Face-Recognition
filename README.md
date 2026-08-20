🎓 Smart Attendance System using Real-Time Face Recognition — “Unlocking Identity with Just a Glance.”
I’m thrilled to share the development of a modern, high-tech, Cyberpunk-themed Smart Attendance System designed for educational institutions and modern security environments.

🔧 Technologies & Frameworks Used:
Frontend: Vanilla JavaScript + Vite + HTML5 WebRTC & Canvas API
Backend: Python 3 + Flask + Flask-CORS
Graphics/UI: Three.js (for rendering the 3D rotating cyberpunk wireframe head background)
Face Detection: Haar Cascade Face Detector (haarcascade_frontalface_default.xml)
Face Recognition: Local Binary Patterns Histograms (LBPH) Face Recognizer (cv2.face.LBPHFaceRecognizer)
Model Serialization: YAML & NumPy (face_model.yml, labels.npy)
Database: SQLite3 (attendance.db) for storing student and attendance logs
🧠 Core Features:
✅ Browser-Based WebRTC Capture: The webcam stream runs entirely inside the user's browser (no server GUI dependencies), making it fully compatible with cloud hosting (Render/Netlify).
✅ Face Registration: Input details and capture 40 high-quality face images locally through the browser webcam with an interactive on-screen percentage indicator.
✅ Real-Time Recognition HUD: Tracks face coordinates and draws a green scanner overlay showing student names and confidence scores in bold, un-mirrored 18px neon fonts.
✅ Automated Attendance: Matches face features against the local LBPH model, monitors consecutive frames for secure verification, and automatically logs present status.
✅ Model Retraining: The backend automatically retrains the LBPH model the instant a new student registration is completed.
✅ Attendance Dashboard: Real-time stats dashboard displaying Total Students, Present Today, overall Attendance Rate, and searchable student log tables.
📂 Database Integration (SQLite):
Students Table: Name, Roll Number, Registration Number.
Attendance Table: Roll Number, Date, Status (Present/Absent).
Stats Summary: Real-time aggregation of attendance metrics and daily logs.
💡 Why It Matters:
Manual attendance tracking is slow and easily cheated. This system combines Computer Vision, WebGL Graphics (Three.js), and WebRTC Web Technologies to create a zero-install, cloud-ready, and highly secure biometric verification tool — bringing cyberpunk aesthetics and automation to modern classrooms and offices!
