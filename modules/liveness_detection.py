import cv2
import dlib
from scipy.spatial import distance
import numpy as np

class LivenessDetector:
    def __init__(self):
        """Initialize liveness detector"""
        self.detector = dlib.get_frontal_face_detector()
        
        # Download shape predictor from:
        # http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 3
        self.blink_counter = 0
        self.total_blinks = 0
    
    def eye_aspect_ratio(self, eye):
        """Calculate Eye Aspect Ratio"""
        # Vertical eye landmarks
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        
        # Horizontal eye landmark
        C = distance.euclidean(eye[0], eye[3])
        
        # Eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, frame):
        """Detect eye blink"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector(gray, 0)
        
        for face in faces:
            # Get facial landmarks
            landmarks = self.predictor(gray, face)
            
            # Extract eye coordinates
            left_eye = []
            right_eye = []
            
            # Left eye landmarks (36-41)
            for n in range(36, 42):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                left_eye.append((x, y))
            
            # Right eye landmarks (42-47)
            for n in range(42, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                right_eye.append((x, y))
            
            # Calculate EAR for both eyes
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Check for blink
            if ear < self.EYE_AR_THRESH:
                self.blink_counter += 1
            else:
                if self.blink_counter >= self.EYE_AR_CONSEC_FRAMES:
                    self.total_blinks += 1
                self.blink_counter = 0
            
            return self.total_blinks > 0
        
        return False
    
    def detect_head_movement(self, frame, prev_frame):
        """Detect head movement (simple method)"""
        if prev_frame is None:
            return False
        
        # Calculate frame difference
        diff = cv2.absdiff(frame, prev_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Calculate movement
        movement = np.sum(gray_diff)
        
        # Threshold for movement detection
        return movement > 1000000
    
    def check_liveness(self, frame, prev_frame=None):
        """Complete liveness check"""
        blink_detected = self.detect_blink(frame)
        movement_detected = False
        
        if prev_frame is not None:
            movement_detected = self.detect_head_movement(frame, prev_frame)
        
        return blink_detected or movement_detected