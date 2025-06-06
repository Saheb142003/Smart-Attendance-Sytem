# 👨‍🎓 Smart Face Recognition Attendance System

This is a Python + Flask-based Smart Student Attendance System that uses Face Recognition to automate student registration, attendance marking, and visualization. It includes a web interface for easy access to student and attendance records, as well as dynamic execution of key functionalities.

---

## 🔧 Features

- 📷 Register student faces using webcam (`add_faces.py`)
- 📚 Browse branches, sections, and students
- 🧑‍💼 View individual student details with best face image
- 📡 Mark attendance with live face recognition (`run_attendance.py`)
- 📥 Download generated attendance files
- 🌐 Beautiful and responsive web interface (HTML + CSS)

---

## 🗂️ Project Structure
```
smart-attendance/
            ├── app.py
            ├── add*faces.py
            ├── view_student.py
            ├── run_attendance.py
            ├── download_attendance.py
            ├── registered_faces/
            │ └── [branch]/[section]/[student]/info.json + faces/
            ├── Attendance/
            │ └── [branch]/[date].csv
            ├── templates/
            │ ├── app.html
            │ ├── index.html
            │ ├── sections.html
            │ ├── student.html
            │ ├── student_details.html
            │ └── attendance*\* # attendance_branches.html, attendance_files.html, etc.
            ├── static/
            │ └── style.css

---
```

## 🚀 Getting Started

### 1. Clone the Repository

git clone (https://github.com/Saheb142003/Smart-Attendance-Sytem)
cd smart-attendance

### 2. Install Requirements

Make sure you have Python 3.8+ installed. Then:
pip install -r requirements.txt
Requirements may include:
-flask
-opencv-python
-face-recognition
-numpy
-Pillow

### 3. Run the App

python app.py
Open your browser and go to:
http://127.0.0.1:5000

##How to use

Add Student Faces → opens webcam to capture images

View Registered Students → lists student data

Run Attendance → starts recognition loop

🔹 Student Details
Click a student's name to view:

ID, Roll, Branch, Section, Other Info

Best captured face image

🔹 Attendance CSV
Saved inside Attendance/[branch]/[date].csv

📸 Dependencies for Face Recognition
Make sure these are working:

Webcam

OpenCV (cv2)

dlib (used internally by face_recognition)

## Proper lighting for detection

✨ Future Ideas
Live webcam feed on browser using WebSockets

            Admin login dashboard
            Student Login
            Dowload Attendace
            Auto-email attendance reports
            Mobile version with PWA support

---

🤝 Credits
Developed by Md Sahebuddin Ansari
Technologies: Python, Flask, OpenCV, Face Recognition, HTML, CSS, JavaScript

📬 Contact
📧 saheb142003@gmail.com
🔗 LinkedIn-https://www.linkedin.com/in/saheb142003/
