import tkinter as tk
from tkinter import messagebox
from modules.database import AttendanceDatabase
from modules.face_recognition_module import FaceRecognizer
from modules.attendance import AttendanceManager
from gui.main_window import MainWindow
from gui.reports import ReportsWindow
from gui.registration import RegistrationWindow
import os

def main():
    """Main application entry point"""
    # Create necessary directories
    os.makedirs('data/database', exist_ok=True)
    os.makedirs('data/student_images', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Check for dlib model
    if not os.path.exists('models/shape_predictor_68_face_landmarks.dat'):
        print("Warning: shape_predictor_68_face_landmarks.dat not found")
        print("Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
    
    # Initialize components
    print("Initializing database...")
    database = AttendanceDatabase()
    
    print("Loading face recognizer...")
    face_recognizer = FaceRecognizer(database)
    
    print("Initializing attendance manager...")
    attendance_manager = AttendanceManager(database)
    
    # Create main menu
    root = tk.Tk()
    root.title("Face Recognition Attendance System - Main Menu")
    root.geometry("500x400")
    
    # Title
    title = tk.Label(
        root,
        text="Attendance System",
        font=("Arial", 24, "bold"),
        bg="#1e3a8a",
        fg="white",
        pady=20
    )
    title.pack(fill=tk.X)
    
    # Menu frame
    menu_frame = tk.Frame(root)
    menu_frame.pack(expand=True, pady=40)
    
    # Buttons
    def open_main_window():
        root.withdraw()
        app = MainWindow(root, database, face_recognizer, attendance_manager)
        app.run()
    
    def open_registration():
        RegistrationWindow(root, database, face_recognizer)
    
    tk.Button(
        menu_frame,
        text="Mark Attendance",
        command=open_main_window,
        bg="#10b981",
        fg="white",
        font=("Arial", 16),
        width=20,
        pady=10
    ).pack(pady=10)
    
    tk.Button(
        menu_frame,
        text="Register Student",
        command=open_registration,
        bg="#3b82f6",
        fg="white",
        font=("Arial", 16),
        width=20,
        pady=10
    ).pack(pady=10)
    
    tk.Button(
        menu_frame,
        text="View Reports",
        command=lambda: ReportsWindow(root, database),
        bg="#f59e0b",
        fg="white",
        font=("Arial", 16),
        width=20,
        pady=10
    ).pack(pady=10)
    
    tk.Button(
        menu_frame,
        text="Exit",
        command=root.quit,
        bg="#ef4444",
        fg="white",
        font=("Arial", 16),
        width=20,
        pady=10
    ).pack(pady=10)
    
    print("\nSystem ready!")
    root.mainloop()

if __name__ == "__main__":
    main()