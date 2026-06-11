from datetime import datetime, timedelta

class AttendanceManager:
    def __init__(self, database):
        """Initialize attendance manager"""
        self.database = database
        self.marked_today = set()  # Track who's been marked today
        self.last_marked_time = {}  # Prevent duplicate marking
        self.MARK_COOLDOWN = 300  # 5 minutes cooldown
    
    def can_mark_attendance(self, student_id):
        today = str(datetime.now().date())
        conn = self.database.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT attendance_id FROM attendance WHERE student_id = ? AND date = ?',
            (student_id, today)
        )
        result = cursor.fetchone()
        conn.close()
        return result is None
    
    def mark_attendance(self, student_id, confidence_score):
        if not self.can_mark_attendance(student_id):
            return False, "Already marked recently"

        conn = self.database.create_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        now = datetime.now().strftime('%H:%M:%S')

        cursor.execute(
            'INSERT INTO attendance (student_id, date, time, confidence_score) VALUES (?, ?, ?, ?)',
            (student_id, today, now, confidence_score)
        )
        conn.commit()
        conn.close()

        self.last_marked_time[student_id] = datetime.now()
        self.marked_today.add(student_id)
        return True, "Attendance marked successfully"
    
    def get_today_attendance(self):
        conn = self.database.create_connection()
        cursor = conn.cursor()
        
        today = str(datetime.now().date())
        print(f"Querying for date: {today}")
        
        # Check what dates are actually in the DB
        cursor.execute('SELECT student_id, date, time FROM attendance')
        print(f"All attendance rows: {cursor.fetchall()}")
        
        # Add this debug line before the JOIN query:
        cursor.execute('SELECT * FROM students')
        print(f"All students: {cursor.fetchall()}")

        cursor.execute('''
            SELECT s.name, s.roll_number, a.date, a.time, a.confidence_score
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.time DESC
        ''', (today,))
        
        records = cursor.fetchall()
        print(f"Matched records: {records}")
        conn.close()
        return records