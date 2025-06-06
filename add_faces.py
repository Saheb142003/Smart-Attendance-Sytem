import cv2
import numpy as np
import os
import json

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1] * imageA.shape[2])
    return err

def check_id_duplicate(student_id):
    base_path = 'registered_faces'
    if not os.path.exists(base_path):
        return (False, "")
    for year in os.listdir(base_path):
        year_path = os.path.join(base_path, year)
        if not os.path.isdir(year_path):
            continue
        for branch in os.listdir(year_path):
            branch_path = os.path.join(year_path, branch)
            if not os.path.isdir(branch_path):
                continue
            for section in os.listdir(branch_path):
                section_path = os.path.join(branch_path, section)
                if not os.path.isdir(section_path):
                    continue
                for student_folder in os.listdir(section_path):
                    info_path = os.path.join(section_path, student_folder, 'info.json')
                    if os.path.exists(info_path):
                        with open(info_path, 'r') as f:
                            info = json.load(f)
                            if info['id'] == student_id:
                                return (True, f"Duplicate ID found for student: {info['name']} with ID {student_id}")
    return (False, "")

def check_roll_duplicate(roll_no, year, branch, section):
    base_path = 'registered_faces'
    section_path = os.path.join(base_path, year, branch, section)
    if not os.path.exists(section_path):
        return (False, "")
    for student_folder in os.listdir(section_path):
        info_path = os.path.join(section_path, student_folder, 'info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
                if info['roll'] == roll_no:
                    return (True, f"Duplicate Roll No found for student: {info['name']} with Roll No {roll_no} in {year}/{branch}/{section}")
    return (False, "")

def check_face_duplicate(new_faces, threshold=1000):
    base_path = 'registered_faces'
    if not os.path.exists(base_path):
        return (False, "")
    for year in os.listdir(base_path):
        year_path = os.path.join(base_path, year)
        if not os.path.isdir(year_path):
            continue
        for branch in os.listdir(year_path):
            branch_path = os.path.join(year_path, branch)
            if not os.path.isdir(branch_path):
                continue
            for section in os.listdir(branch_path):
                section_path = os.path.join(branch_path, section)
                if not os.path.isdir(section_path):
                    continue
                for student_folder in os.listdir(section_path):
                    faces_folder = os.path.join(section_path, student_folder, 'faces')
                    if os.path.exists(faces_folder):
                        for face_file in os.listdir(faces_folder):
                            existing_face_path = os.path.join(faces_folder, face_file)
                            existing_face = cv2.imread(existing_face_path)
                            for new_face in new_faces:
                                if existing_face.shape != new_face.shape:
                                    continue
                                error = mse(existing_face, new_face)
                                if error < threshold:
                                    info_path = os.path.join(section_path, student_folder, 'info.json')
                                    with open(info_path, 'r') as f:
                                        info = json.load(f)
                                    return (True, f"Face similar to existing student {info['name']} (ID: {info['id']})")
    return (False, "")

def register_student():
    facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    video = cv2.VideoCapture(0)

    print("=== Enter Student Details ===")
    name = input("Name: ").strip()
    student_id = input("Student ID: ").strip()
    roll_no = input("Roll Number: ").strip()
    email = input("Email: ").strip()
    year = input("Year (e.g., 2023): ").strip()
    branch = input("Branch: ").strip()
    section = input("Section: ").strip()

    duplicate_id_found, message_id = check_id_duplicate(student_id)
    if duplicate_id_found:
        print(f"Duplicate Found! {message_id}")
        choice = input("Quit registration? (y/n): ").lower()
        if choice == 'y':
            video.release()
            cv2.destroyAllWindows()
            print("Registration cancelled.")
            return False

    duplicate_roll_found, message_roll = check_roll_duplicate(roll_no, year, branch, section)
    if duplicate_roll_found:
        print(f"Duplicate Found! {message_roll}")
        choice = input("Quit registration? (y/n): ").lower()
        if choice == 'y':
            video.release()
            cv2.destroyAllWindows()
            print("Registration cancelled.")
            return False

    faces_data = []
    i = 0
    print("\nStarting face capture. Press 'q' to quit.")

    while True:
        ret, frame = video.read()
        if not ret:
            print("Failed to grab frame from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            crop_img = frame[y:y+h, x:x+w, :]
            resized_img = cv2.resize(crop_img, (50,50))

            if len(faces_data) < 100 and i % 10 == 0:
                faces_data.append(resized_img)
            i += 1

            cv2.putText(frame, f"Faces Captured: {len(faces_data)}", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

        cv2.imshow("Face Capture - Press q to quit", frame)
        k = cv2.waitKey(1)
        if k == ord('q') or len(faces_data) == 100:
            break

    video.release()
    cv2.destroyAllWindows()

    if len(faces_data) == 0:
        print("No faces captured, aborting registration.")
        return False

    faces_data_np = np.array(faces_data)

    face_duplicate, face_msg = check_face_duplicate(faces_data_np)
    if face_duplicate:
        print(f"Duplicate Found! {face_msg}")
        choice = input("Quit registration? (y/n): ").lower()
        if choice == 'y':
            print("Registration cancelled.")
            return False

    base_dir = 'registered_faces'
    student_folder_name = f"{roll_no}_{name.replace(' ', '_')}"
    student_folder_path = os.path.join(base_dir, year, branch, section, student_folder_name)
    faces_folder_path = os.path.join(student_folder_path, 'faces')

    os.makedirs(faces_folder_path, exist_ok=True)

    for idx, face_img in enumerate(faces_data_np, start=1):
        face_img_path = os.path.join(faces_folder_path, f"face_{idx}.png")
        cv2.imwrite(face_img_path, face_img)

    info = {
        "name": name,
        "id": student_id,
        "roll": roll_no,
        "email": email,
        "branch": branch,
        "section": section,
        "year": year
    }
    info_path = os.path.join(student_folder_path, 'info.json')
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=4)

    print(f"Student {name} registered successfully with {len(faces_data_np)} face images saved.")
    return True

def main():
    while True:
        success = register_student()
        if not success:
            choice = input("Do you want to try registering another student? (y/n): ").lower()
            if choice != 'y':
                print("Exiting registration.")
                break
            else:
                continue
        else:
            choice = input("Register another student? (y/n): ").lower()
            if choice != 'y':
                print("Exiting registration.")
                break

if __name__ == '__main__':
    main()
