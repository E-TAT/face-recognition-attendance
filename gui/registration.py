import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk

class RegistrationWindow:
    def __init__(self, parent, database, face_recognizer):
        """Initialize registration window"""
        self.database = database
        self.parent = parent
        self.face_recognizer = face_recognizer
        
        self.window = tk.Toplevel()
        self.window.title("Student Registration")
        self.window.geometry("800x600")
        
        self.captured_image = None
        self.preview_photo = None  # To keep reference
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create registration form"""
        # Title
        title = tk.Label(
            self.window,    
            text="Register New Student",
            font=("Arial", 20, "bold"),
            bg="#3b82f6",
            fg="white",
            pady=15
        )
        title.pack(fill=tk.X)
        
        # Main container with scrollbar in case content overflows
        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling if needed
        canvas = tk.Canvas(main_container)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form frame (now inside scrollable frame)
        form_frame = tk.Frame(scrollable_frame)
        form_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        # Roll Number
        tk.Label(form_frame, text="Roll Number:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.roll_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.roll_entry.grid(row=0, column=1, pady=10, padx=(10, 0))
        
        # Name
        tk.Label(form_frame, text="Name:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.name_entry.grid(row=1, column=1, pady=10, padx=(10, 0))
        
        # Class
        tk.Label(form_frame, text="Class:", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.class_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.class_entry.grid(row=2, column=1, pady=10, padx=(10, 0))
        
        
        # Photo label and buttons
        tk.Label(form_frame, text="Photo:", font=("Arial", 12)).grid(row=4, column=0, sticky=tk.W, pady=10)
        
        photo_btn_frame = tk.Frame(form_frame)
        photo_btn_frame.grid(row=4, column=1, pady=10, padx=(10, 0), sticky=tk.W)
        
        tk.Button(
            photo_btn_frame,
            text="Capture Photo",
            command=self.capture_photo,
            bg="#10b981",
            fg="white",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            photo_btn_frame,
            text="Upload Photo",
            command=self.upload_photo,
            bg="#3b82f6",
            fg="white",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Photo preview
        preview_label = tk.Label(form_frame, text="Preview:", font=("Arial", 12))
        preview_label.grid(row=5, column=0, sticky=tk.W, pady=10)
        
        # Preview container with fixed size
        preview_container = tk.Frame(form_frame, bg="lightgray", width=400, height=250, relief=tk.SUNKEN, bd=2)
        preview_container.grid(row=5, column=1, pady=10, padx=(10, 0))
        preview_container.grid_propagate(False)
        
        self.photo_label = tk.Label(preview_container, bg="lightgray", text="No photo captured", font=("Arial", 10))
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        
        # Register button - NOW IN ITS OWN ROW
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=30)
        
        self.register_btn = tk.Button(
            button_frame,
            text="Register Student",
            command=self.register_student,
            bg="#1e3a8a",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=40,
            pady=12,
            cursor="hand2"
        )
        self.register_btn.pack()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(
            form_frame,
            text="← Back",
            command=self.window.destroy,
            bg="#6b7280", fg="white", font=("Arial", 11), padx=15
        ).grid(row=7, column=0, columnspan=2, pady=5)
    
    def capture_photo(self):
        """Open camera to capture photo"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open camera")
            return

        popup = tk.Toplevel(self.window)
        popup.title("Capture Photo")
        popup.geometry("500x400")
        
        # Video label
        video_label = tk.Label(popup, bg="black")
        video_label.pack(padx=10, pady=10)
        
        # Flag to control video loop
        self.capturing = True
        
        def update_frame():
            if not self.capturing:
                return
                
            ret, frame = cap.read()
            if ret:
                # Convert frame for display
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = cv2.resize(rgb, (400, 300))
                img = Image.fromarray(rgb)
                photo = ImageTk.PhotoImage(img)
                
                video_label.config(image=photo)
                video_label.image = photo  # Keep reference
                
                # Store the original frame for capture
                self.current_frame = frame.copy()
                
            popup.after(33, update_frame)
        
        def capture():
            if hasattr(self, 'current_frame'):
                self.captured_image = self.current_frame.copy()
                self.show_captured_image(self.captured_image)
            self.capturing = False
            cap.release()
            popup.destroy()
        
        def cancel():
            self.capturing = False
            cap.release()
            popup.destroy()
        
        # Buttons
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Capture", command=capture,
                 bg="#10b981", fg="white", font=("Arial", 12), padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=cancel,
                 bg="#ef4444", fg="white", font=("Arial", 12), padx=20).pack(side=tk.LEFT, padx=5)
        
        # Start video
        update_frame()
        
        popup.protocol("WM_DELETE_WINDOW", lambda: [cap.release(), popup.destroy()])
    
    def upload_photo(self):
        """Upload photo from file"""
        file_path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            try:
                # Read image with OpenCV
                image = cv2.imread(file_path)
                if image is not None:
                    self.captured_image = image
                    self.show_captured_image(image)
                else:
                    messagebox.showerror("Error", "Could not read image file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def show_captured_image(self, image):
        """Display captured/uploaded image in preview"""
        if image is None:
            messagebox.showerror("Error", "Could not load image.")
            return
        
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get the preview container size (approximately)
            preview_width = 400
            preview_height = 250
            
            # Calculate aspect ratio
            h, w = image_rgb.shape[:2]
            aspect = w / h
            
            # Resize maintaining aspect ratio
            if w > h:
                new_w = preview_width
                new_h = int(preview_width / aspect)
            else:
                new_h = preview_height
                new_w = int(preview_height * aspect)
            
            # Ensure dimensions don't exceed container
            if new_w > preview_width:
                new_w = preview_width
                new_h = int(new_w / aspect)
            if new_h > preview_height:
                new_h = preview_height
                new_w = int(new_h * aspect)
            
            # Resize image
            image_resized = cv2.resize(image_rgb, (new_w, new_h))
            
            # Convert to PIL Image
            img = Image.fromarray(image_resized)
            
            # Create PhotoImage and keep reference
            self.preview_photo = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.photo_label.config(image=self.preview_photo, text="")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def register_student(self):
        """Register the student"""
        # Validate inputs
        roll = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()
        student_class = self.class_entry.get().strip()
        
        if not roll or not name or not student_class:
            messagebox.showerror("Error", "Please fill all required fields (Roll, Name, Class)")
            return
        
        if self.captured_image is None:
            messagebox.showerror("Error", "Please capture or upload a photo")
            return
        
        # Add student to database
        student_id = self.database.add_student(roll, name, student_class)
        
        if student_id is None:
            messagebox.showerror("Error", "Student with this roll number already exists")
            return
        
        # Generate and save face encoding
        success = self.face_recognizer.register_new_face(self.captured_image, student_id)
        
        if success:
            messagebox.showinfo("Success", f"Student {name} registered successfully!")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to detect face in the image. Please try again with a clearer photo.")