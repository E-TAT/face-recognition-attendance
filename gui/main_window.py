import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
from modules.liveness import LivenessDetector

class MainWindow:
    def __init__(self, parent, database, face_recognizer, attendance_manager):
        self.parent = parent
        self.after_id = None
        self.database = database
        self.face_recognizer = face_recognizer
        self.face_recognizer.load_known_faces()
        self.attendance_manager = attendance_manager
        self._notified = set()
        self.liveness_detector = LivenessDetector()
        
        self.root = tk.Tk()
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x700")
        
        self.camera_running = False
        self.cap = None
        self.current_image = None
        
        self.create_widgets()
        self._photos = []
        
        # Start update loop for displaying frames
        self.update_display()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.refresh_attendance() 
        self.root.mainloop()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root, 
            text="Attendance System using Face Recognition",
            font=("Arial", 24, "bold"),
            bg="#1e3a8a",
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=5)
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Camera
        left_panel = tk.Frame(main_frame, bg="lightgray", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Camera label
        self.camera_label = tk.Label(left_panel, bg="black", text="Camera Off", 
                                     fg="white", font=("Arial", 16))
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera controls
        camera_controls = tk.Frame(left_panel)
        camera_controls.pack(pady=10)
        
        self.start_btn = tk.Button(
            camera_controls,
            text="Start Camera",
            command=self.start_camera,
            bg="#10b981",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        if not self.face_recognizer.model_loaded:
            self.start_btn.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.NORMAL)
        
        self.stop_btn = tk.Button(
            camera_controls,
            text="Stop Camera",
            command=self.stop_camera,
            bg="#ef4444",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Attendance list
        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Attendance title
        att_title = tk.Label(
            right_panel,
            text="Today's Attendance",
            font=("Arial", 16, "bold")
        )
        att_title.pack(pady=10)
        
        # Attendance table
        self.attendance_tree = ttk.Treeview(
            right_panel,
            columns=("Name", "Roll", "Date", "Time", "Confidence"),
            show="headings",
            height=20
        )
        
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Roll", text="Roll Number")
        self.attendance_tree.heading("Date", text="Date")
        self.attendance_tree.heading("Time", text="Time")
        self.attendance_tree.heading("Confidence", text="Confidence")
        
        self.attendance_tree.column("Name", width=150)
        self.attendance_tree.column("Roll", width=100)
        self.attendance_tree.column("Date", width=100)
        self.attendance_tree.column("Time", width=100)
        self.attendance_tree.column("Confidence", width=100)
        
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        refresh_btn = tk.Button(
            right_panel,
            text="Refresh",
            command=self.refresh_attendance,
            bg="#3b82f6",
            fg="white",
            font=("Arial", 11),
            padx=15,
            pady=5
        )
        refresh_btn.pack(pady=10)
        if self.face_recognizer.model_loaded:
            self.status_label.config(
                text="✓ Model loaded successfully.",
                fg="green"
            )
        else:
            self.status_label.config(
                text="⚠ No trained model found.",
                fg="red"
            )          
        print("Start button state after setup:", self.start_btn["state"])
        
        tk.Button(
            self.root,
            text="← Back to Menu",
            command=self.on_closing,
            bg="#6b7280", fg="white", font=("Arial", 11), padx=15, pady=5
        ).pack(pady=5)
    
    def start_camera(self):
        self.face_recognizer.load_known_faces()
        if not self.face_recognizer.model_loaded:
            messagebox.showwarning("Model Not Found", "Please register students first.")
            return

        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="🎥 Opening camera…", fg="blue")
        
        # Move everything into the thread so UI doesn't freeze
        threading.Thread(target=self._init_camera, daemon=True).start()

    def _init_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", "Could not open camera."))
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            return
            # Warmup — discard first few frames
        for _ in range(5):
            cap.read()
        self.cap = cap
        self.camera_running = True
        self.root.after(0, lambda: self.stop_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_label.config(text="🎥 Camera running…", fg="blue"))
        self.camera_loop()  # runs the existing loop directly
    
    def stop_camera(self):
        self.camera_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.cap:
            self.cap.release()
        
        self.camera_label.config(image='', text="Camera Off")
        self.current_image = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        self.liveness_detector.reset_all()
        self._notified.clear()
    
    def camera_loop(self):
        """Main camera processing loop"""
        while self.camera_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            
            self.current_image = frame.copy()

            # Recognize faces
            recognized_faces = self.face_recognizer.recognize_faces(frame)
            
            # Process each face
            for face_data in recognized_faces:
                location = face_data['location']
                name = face_data['name']
                student_id = face_data['student_id']
                confidence = face_data['confidence']

                top, left, bottom, right = location

                # Check liveness
                if student_id:
                    liveness = self.liveness_detector.check(student_id, location)
                else:
                    liveness = 'checking'

                # Pick box color based on liveness
                if liveness == 'live':
                    color = (0, 255, 0)       # green - live
                    status_text = "LIVE"
                elif liveness == 'failed':
                    color = (0, 0, 255)       # red - spoof
                    status_text = "SPOOF?"
                else:
                    color = (0, 165, 255)     # orange - checking
                    status_text = "Move head..."

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                display_label = f"{name} ({confidence:.0%}) [{status_text}]"
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, display_label, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

                # Only mark attendance if live
                if student_id and confidence > 0.3 and liveness == 'live' and student_id not in self._notified:
                    success, message = self.attendance_manager.mark_attendance(student_id, confidence)
                    self._notified.add(student_id)
                    self.liveness_detector.reset(student_id)
                    if success:
                        self.root.after(500, self.refresh_attendance)
                        self.root.after(0, lambda n=name: messagebox.showinfo("Attendance Marked", f"✓ Attendance marked for {n}!"))
                    else:
                        self.root.after(0, lambda n=name: messagebox.showwarning("Already Marked", f"⚠ {n} already marked today!"))                 
            
            # Store frame for display
            self.current_image = frame.copy()
    
    def update_display(self):
        if self.root.winfo_exists() and self.camera_label.winfo_exists():
            if self.current_image is not None:
                try:
                    frame = self.current_image.copy()
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb).resize((640, 480), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img, master=self.root)
                    self._photos = [photo]  # keep only latest, clears old ones
                    self.camera_label.configure(image=photo, text="")
                    self.camera_label.image = photo
                except Exception as e:
                    print(f"Display error: {e}")
        
        self.after_id = self.root.after(33, self.update_display)
    
    def refresh_attendance(self):
        """Refresh attendance list"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Get today's attendance
        records = self.attendance_manager.get_today_attendance()
        
        # Add to tree
        for name, roll, date, time, confidence in records:
            time_str = str(time)[:8]
            conf_str = f"{confidence:.0%}" if confidence else "N/A"
            self.attendance_tree.insert("", 0, values=(name, roll, date, time_str, conf_str))
    
    
    def on_closing(self):
        self.stop_camera()
        self.root.destroy()
        self.parent.deiconify()