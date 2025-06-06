import subprocess
import webbrowser
import threading

def main_menu():
    while True:
        print("\n==========================")
        print("  Student Attendance App")
        print("==========================")
        print("1. Add Student Faces")
        print("2. Run Attendance")
        print("3. Download Attendance")
        print("4. View Registered Students")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            subprocess.run(["python", "add_faces.py"])
        elif choice == '2':
            subprocess.run(["python", "run_attendance.py"])
        elif choice == '3':
            print("\n[✔] Web link to download attendance:")
            print("➡️  http://127.0.0.1:5000/attendance")
            webbrowser.open("http://127.0.0.1:5000/attendance")
            # Ensure the Flask app serving attendance is already running, or run it here if needed
        elif choice == '4':
            print("\n[✔] Launching registered students viewer (Flask)...")
            # Run the view_student.py Flask app in a thread or subprocess
            # Here using subprocess so it keeps running separately
            subprocess.Popen(["python", "view_student.py"])
            webbrowser.open("http://127.0.0.1:5000/")
            # Don't exit menu immediately so user can come back or exit manually
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
