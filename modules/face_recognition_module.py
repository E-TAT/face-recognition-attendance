import cv2
import numpy as np
import os
import pickle

class FaceRecognizer:
    def __init__(self, database):
        self.database = database
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_names = {}
        self.known_faces = {}
        self.model_loaded = False   
        self.load_known_faces()

    def save_model(self):
        self.recognizer.save('data/face_model.yml')
        with open('data/face_labels.pkl', 'wb') as f:
            pickle.dump({'known_faces': self.known_faces, 'known_names': self.known_names}, f)
        self.model_loaded = True

    def load_known_faces(self):
        if os.path.exists('data/face_model.yml') and os.path.exists('data/face_labels.pkl'):
            self.recognizer.read('data/face_model.yml')
            with open('data/face_labels.pkl', 'rb') as f:
                data = pickle.load(f)
            self.known_faces = data['known_faces']
            self.known_names = data['known_names']
            self.model_loaded = True
        else:
            self.model_loaded = False
    
    def generate_face_encoding(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)  # ADD THIS - helps with lighting
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,   # was 1.3, lower = more sensitive
            minNeighbors=3,    # was 5, lower = more sensitive
            minSize=(30, 30)   # was maybe larger
        )

        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            return face_roi, (x, y, w, h)
        return None, None
    
    def register_new_face(self, image, student_id):
        face_roi, location = self.generate_face_encoding(image)
        
        if face_roi is None:
            return False
        
        conn = self.database.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        name = result[0]
        
        # Define label and resize BEFORE using them
        label = int(student_id)
        face_roi_resized = cv2.resize(face_roi, (200, 200))
        
        is_first = len(self.known_faces) == 0
        self.known_faces[label] = student_id
        self.known_names[label] = name
        
        if is_first:
            self.recognizer.train([face_roi_resized], np.array([label]))
        else:
            self.recognizer.update([face_roi_resized], np.array([label]))
        
        self.save_model()
        return True
    
    def recognize_faces(self, frame):
        """Recognize faces in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)

        faces = self.face_cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,   # match the test
            minNeighbors=4,     # match the test
            minSize=(60, 60)    # match the test
        )
        
        recognized_faces = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi_resized = cv2.resize(face_roi, (200, 200))
            
            try:
                label, confidence = self.recognizer.predict(face_roi_resized)
                
                # Lower confidence = better match (0 = perfect match)
                # Convert to percentage where higher = better
                confidence_percent = max(0, (100 - confidence) / 100)
                
                THRESHOLD = 100
                confidence_percent = max(0, (THRESHOLD - confidence) / THRESHOLD)
                if confidence < THRESHOLD:
                    name = self.known_names.get(label, "Unknown")
                    student_id = self.known_faces.get(label)
                else:
                    name = "Unknown"
                    student_id = None
                    confidence_percent = 0
                
                recognized_faces.append({
                    'location': (y, x, y+h, x+w),  # top, right, bottom, left
                    'name': name,
                    'student_id': student_id,
                    'confidence': confidence_percent
                })
            except:
                # No trained model yet
                recognized_faces.append({
                    'location': (y, x, y+h, x+w),
                    'name': "Unknown",
                    'student_id': None,
                    'confidence': 0
                })
        
        return recognized_faces