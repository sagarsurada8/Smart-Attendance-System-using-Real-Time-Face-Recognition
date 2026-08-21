# Smart Attendance System using Real-Time Face Recognition

A modern, high-tech, Cyberpunk-themed Web application featuring **HTML5 WebRTC client-side camera streaming** and a **Python Flask backend** powered by OpenCV's Local Binary Patterns Histograms (LBPH) Face Recognition algorithm.

---

## 🚀 Key Features

* **HTML5 WebRTC Webcam Stream**: Eliminates server-side camera window dependencies. The webcam streams directly inside the browser using standard browser APIs, making it fully deployable to standard cloud hosting servers.
* **Canvas Face Bounding Box & HUD**: Draws green face tracking frames, target overlays, scan lines, and user names/confidence percentages directly on the web canvas in real-time.
* **Smart Mirror Interaction**: The video stream is naturally mirrored for the user, while the face bounding boxes and text overlays are dynamically calculated to render **non-mirrored and fully readable** in a bold 18px neon HUD interface.
* **Add Student (Registration)**: Saves student metadata (Name, Roll, Reg No), captures 40 face frames sequentially (with on-screen progress indicator), and triggers immediate training of the LBPH face model.
* **Take Attendance (Recognition)**: Scans the user's face, matches it against the database using a custom confidence score, tracks consecutive matches for security verification, and logs attendance into an SQLite database.
* **Attendance Dashboard**: Displays real-time metrics (Total Students, Present Today, Attendance Rate) and provides searchable, scrollable tables listing all registered students and today's attendance logs.
* **Custom Cyberpunk UI**: Features a 3D rotating wireframe head background powered by Three.js, glowing neon border interfaces, and custom styling.

---

## 🛠️ Tech Stack

* **Frontend**: HTML5 Video & Canvas, CSS3 custom animations, Vanilla JavaScript, Vite, Three.js (3D graphics rendering).
* **Backend**: Python 3, Flask, Flask-CORS, OpenCV (`cv2.face` module), NumPy, SQLite3.

---

## 📦 Directory Structure

```
.
├── backend/
│   ├── app.py                # Main Flask Web API Entrypoint
│   ├── database.py           # SQLite Database Creation and Handlers
│   ├── recognize.py          # Dynamic LBPH Face Recognition Engine
│   └── train_model.py        # LBPH Model Training and Serialization Script
├── data/
│   ├── attendance.db         # Local SQLite Database (auto-generated)
│   └── faces/                # Cropped face images of registered students (auto-generated)
├── frontend/
│   ├── index.html            # Core Cyberpunk Landing Interface & Modals
│   ├── package.json          # Node.js Dependencies & Scripts
│   ├── src/
│   │   ├── main.js           # Three.js 3D logic & WebRTC streaming controls
│   │   └── style.css         # Neon HUD styles & Modal layouts
├── models/
│   ├── face_model.yml        # Serialized LBPH Face Model (auto-generated)
│   ├── labels.npy            # Name mappings matching LBPH labels (auto-generated)
│   └── haarcascade_frontalface_default.xml # Haar Cascade face detector
├── netlify.toml              # Netlify Deployment Configuration
└── requirements.txt          # Python headless dependencies for Cloud Deployment
```

---

## 💻 Local Setup Guide

### 1. Backend Installation (Python)

1. Navigate to the root directory and create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   * **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
   * **Windows (CMD)**: `.\venv\Scripts\activate.bat`
   * **Linux/macOS**: `source venv/bin/activate`
3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   python backend/app.py
   ```
   *The server will run on `http://localhost:5000`*

### 2. Frontend Installation (Vite/Node)

1. Open a new terminal window and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Launch the Vite dev server:
   ```bash
   npm run dev
   ```
   *The client site will open on `http://localhost:5173`*

---

## ☁️ Cloud Deployment Guide

Because the camera capture occurs locally in the user's browser, the application is designed to be fully deployable to standard cloud hosting servers.

### 1. Deploy the Backend (Render)
1. Link your GitHub repository to your [Render](https://render.com) account.
2. Create a new **Web Service**.
3. Choose the repository and configure:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python backend/app.py`
4. Copy the backend URL (e.g. `https://sagar-face-attendance-2026-v2.onrender.com`).

### 2. Point Frontend to Cloud URL & Deploy (Netlify)
1. Open `frontend/src/main.js` and set the `API_BASE` URL variable (line 987) to your new Render Backend URL:
   ```javascript
   const API_BASE = "https://sagar-face-attendance-2026-v2.onrender.com";
   ```
2. Push your changes to GitHub.
3. Import your project into [Netlify](https://app.netlify.com). Netlify will read the root `netlify.toml` file automatically and deploy your site with the correct configurations!
