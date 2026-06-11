import sqlite3
import pickle
from datetime import datetime

class AttendanceDatabase:
    def __init__(self, db_path='data/database/attendance.db'):
        self.db_path = db_path
        self.create_tables()
    
    def create_connection(self):
        """Create database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create all necessary tables"""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            is_twin BOOLEAN DEFAULT 0,
            twin_sibling_id INTEGER,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (twin_sibling_id) REFERENCES students(student_id)
        )
        ''')
        
        # Face encodings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings (
            encoding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            face_encoding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')
        
        # Attendance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            status TEXT DEFAULT 'Present',
            confidence_score REAL,
            marked_by TEXT DEFAULT 'System',
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student(self, roll_number, name, student_class):
        """Add a new student"""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO students (roll_number, name, class)
            VALUES (?, ?, ?)
            ''', (roll_number, name, student_class))
            
            student_id = cursor.lastrowid
            conn.commit()
            return student_id
        except sqlite3.IntegrityError:
            print(f"Student with roll number {roll_number} already exists")
            return None
        finally:
            conn.close()
    
    def save_face_encoding(self, student_id, face_encoding):
        """Save face encoding for a student"""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        # Convert numpy array to binary
        encoding_blob = pickle.dumps(face_encoding)
        
        cursor.execute('''
        INSERT INTO face_encodings (student_id, face_encoding)
        VALUES (?, ?)
        ''', (student_id, encoding_blob))
        
        conn.commit()
        conn.close()
    
    def get_all_face_encodings(self):
        """Get all face encodings with student info"""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT s.student_id, s.name, s.roll_number, f.face_encoding
        FROM students s
        JOIN face_encodings f ON s.student_id = f.student_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert blob back to numpy array
        encodings = []
        for student_id, name, roll_number, encoding_blob in results:
            encoding = pickle.loads(encoding_blob)
            encodings.append({
                'student_id': student_id,
                'name': name,
                'roll_number': roll_number,
                'encoding': encoding
            })
        
        return encodings
    
    def mark_attendance(self, student_id, confidence_score):
        """Mark attendance for a student"""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        
        # Check if already marked today
        cursor.execute('''
        SELECT * FROM attendance 
        WHERE student_id = ? AND date = ?
        ''', (student_id, current_date))
        
        if cursor.fetchone():
            conn.close()
            return False  # Already marked
        
        # Mark attendance
        cursor.execute('''
        INSERT INTO attendance (student_id, date, time, confidence_score)
        VALUES (?, ?, ?, ?)
        ''', (student_id, current_date, current_time, confidence_score))
        
        conn.commit()
        conn.close()
        return True