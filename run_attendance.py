import cv2
import numpy as np
import pickle
import os
import pandas as pd
from datetime import datetime

# Load face data and labels (ensure paths are correct)
with open('data/faces_data.pkl', 'rb') as f:
    faces_data = pickle.load(f)

with open('data/names.pkl', 'rb') as f:
    labels = pickle.load(f)

faces_data = np.array(faces_data)
labels = np.array(labels)

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
video = cv2.VideoCapture(0)

# Inputs
year = input("Enter Year (e.g. 2024): ").strip()
branch = input("Enter Branch (e.g. CSE): ").strip()
section = input("Enter Section (e.g. A): ").strip()
subject = input("Enter Subject (e.g. Math): ").strip()

print(f"[INFO] Taking attendance for {year}/{branch}/{section} - Subject: {subject}")

# Load all students in registered_faces/year/branch/section
BASE_DIR = "registered_faces"
students_dir = os.path.join(BASE_DIR, year, branch, section)
if not os.path.exists(students_dir):
    print(f"[ERROR] Directory {students_dir} not found!")
    exit(1)

# Load students info: {roll: {name, folder}}
students = {}
for folder in os.listdir(students_dir):
    student_path = os.path.join(students_dir, folder)
    info_path = os.path.join(student_path, 'info.json')
    if os.path.exists(info_path):
        import json
        with open(info_path, 'r') as f:
            info = json.load(f)
        roll = str(info.get('roll', folder))
        name = info.get('name', 'Unknown')
        students[roll] = {
            'name': name,
            'folder': folder
        }

print(f"[INFO] Loaded {len(students)} students.")

# Attendance file path setup
today = datetime.now().strftime("%d%m%Y")
attendance_dir = os.path.join("Attendance", year, branch, section, subject)
os.makedirs(attendance_dir, exist_ok=True)
attendance_file = os.path.join(attendance_dir, f"{today}.xlsx")

# Create attendance DataFrame with all students marked absent initially
df = pd.DataFrame(columns=["Roll No", "Name", "Attendance", "Time"])
for roll, data in students.items():
    df = df.append({
        "Roll No": roll,
        "Name": data['name'],
        "Attendance": "A",
        "Time": ""
    }, ignore_index=True)

# Set for students marked present (store roll numbers)
present_students = set()

print("[INFO] Starting camera. Press 'q' to quit after attendance.")

while True:
    ret, frame = video.read()
    if not ret:
        print("[ERROR] Failed to capture video frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_crop = frame[y:y + h, x:x + w]
        resized = cv2.resize(face_crop, (50, 50)).flatten().reshape(1, -1)

        distances = np.linalg.norm(faces_data - resized, axis=1)
        idx = np.argmin(distances)

        if distances[idx] < 70:  # Adjust threshold if needed
            name_id = labels[idx]
            # Expected format: "Name-Roll"
            if '-' in name_id:
                name, roll = name_id.split('-')
            else:
                # fallback if format differs
                roll = name_id
                name = students.get(roll, {}).get('name', 'Unknown')

            if roll not in present_students and roll in students:
                print(f"[INFO] Marked present: {name} ({roll})")
                present_students.add(roll)

                # Update DataFrame: Attendance = P, Time = current time
                now_time = datetime.now().strftime("%H:%M:%S")
                df.loc[df["Roll No"] == roll, "Attendance"] = "P"
                df.loc[df["Roll No"] == roll, "Time"] = now_time

            cv2.putText(frame, f"{name}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Unknown", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 255), 2)

    cv2.imshow("Attendance System", frame)

    # Quit with 'q'
    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

# Save attendance
df = df.sort_values(by="Roll No")
df.to_excel(attendance_file, index=False)
print(f"[INFO] Attendance saved to {attendance_file}")
print("[INFO] Attendance session ended.")
