import cv2
import face_recognition
import numpy as np

class FaceDetector:
    def __init__(self):
        """Initialize face detector"""
        # Load Haar Cascade (backup method)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces_opencv(self, frame):
        """Detect faces using OpenCV Haar Cascade"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def detect_faces_hog(self, frame):
        """Detect faces using HOG (face_recognition library)"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        
        return face_locations
    
    def detect_faces_cnn(self, frame):
        """Detect faces using CNN (more accurate but slower)"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model='cnn')
        return face_locations
    
    def preprocess_image(self, frame):
        """Preprocess image for better detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for low-light enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Convert back to BGR
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return enhanced_bgr
    
    def draw_face_boxes(self, frame, face_locations, names=None):
        """Draw boxes around detected faces"""
        for i, (top, right, bottom, left) in enumerate(face_locations):
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw name if provided
            if names and i < len(names):
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, names[i], (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame