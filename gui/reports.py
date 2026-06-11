import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class ReportsWindow:
    def __init__(self, parent, database):
        self.database = database
        
        self.window = tk.Toplevel(parent)
        self.window.title("Attendance Reports")
        self.window.geometry("900x600")
        
        self._create_widgets()
        self._load_summary()

    def _create_widgets(self):
        tk.Label(
            self.window,
            text="Attendance Reports",
            font=("Arial", 20, "bold"),
            bg="#1e3a8a", fg="white", pady=15
        ).pack(fill=tk.X)

        # Tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1 - Attendance by date
        self.date_tab = tk.Frame(self.notebook)
        self.notebook.add(self.date_tab, text="Attendance by Date")
        self._create_date_tab()

        # Tab 2 - Per student history
        self.student_tab = tk.Frame(self.notebook)
        self.notebook.add(self.student_tab, text="Student History")
        self._create_student_tab()

        # Tab 3 - Summary
        self.summary_tab = tk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="Summary")
        self._create_summary_tab()

        tk.Button(
            self.window,
            text="← Back",
            command=self.window.destroy,
            bg="#6b7280", fg="white", font=("Arial", 11), padx=15, pady=5
        ).pack(pady=5)

        self.alerts_tab = tk.Frame(self.notebook)
        self.notebook.add(self.alerts_tab, text="⚠ Low Attendance Alerts")
        self._create_alerts_tab()

    def _create_alerts_tab(self):
        ctrl = tk.Frame(self.alerts_tab)
        ctrl.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(ctrl, text="Alert if attendance below:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.threshold_entry = tk.Entry(ctrl, font=("Arial", 11), width=5)
        self.threshold_entry.insert(0, "75")
        self.threshold_entry.pack(side=tk.LEFT, padx=10)
        tk.Label(ctrl, text="%", font=("Arial", 11)).pack(side=tk.LEFT)

        tk.Button(
            ctrl, text="Check",
            command=self._load_alerts,
            bg="#ef4444", fg="white", font=("Arial", 11), padx=10
        ).pack(side=tk.LEFT, padx=10)

        self.alerts_tree = ttk.Treeview(
            self.alerts_tab,
            columns=("Name", "Roll", "Days Present", "Attendance %", "Status"),
            show="headings", height=15
        )
        for col, w in [("Name", 180), ("Roll", 100), ("Days Present", 120), ("Attendance %", 120), ("Status", 150)]:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=w)
        self.alerts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Red tag for low attendance
        self.alerts_tree.tag_configure("low", background="#fee2e2", foreground="#dc2626")
        self.alerts_tree.tag_configure("ok", background="#dcfce7", foreground="#16a34a")

    def _load_alerts(self):
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        try:
            threshold = int(self.threshold_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for threshold.")
            return

        try:
            conn = self.database.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT date) FROM attendance')
            total_days = cursor.fetchone()[0] or 1

            cursor.execute('''
                SELECT s.name, s.roll_number, COUNT(a.attendance_id) as days_present
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.student_id
                ORDER BY days_present ASC
            ''')
            rows = cursor.fetchall()
            conn.close()

            for name, roll, days in rows:
                pct = (days / total_days) * 100
                pct_str = f"{pct:.1f}%"
                if pct < threshold:
                    status = "⚠ LOW ATTENDANCE"
                    tag = "low"
                else:
                    status = "✓ OK"
                    tag = "ok"
                self.alerts_tree.insert("", "end", values=(name, roll, days, pct_str, status), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------ Tab 1
    def _create_date_tab(self):
        ctrl = tk.Frame(self.date_tab)
        ctrl.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(ctrl, text="Select Date:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.date_entry = tk.Entry(ctrl, font=("Arial", 11), width=15)
        self.date_entry.insert(0, str(date.today()))
        self.date_entry.pack(side=tk.LEFT, padx=10)

        tk.Button(
            ctrl, text="Search",
            command=self._search_by_date,
            bg="#3b82f6", fg="white", font=("Arial", 11), padx=10
        ).pack(side=tk.LEFT)

        self.date_count_lbl = tk.Label(ctrl, text="", font=("Arial", 11, "bold"), fg="#1e3a8a")
        self.date_count_lbl.pack(side=tk.LEFT, padx=20)

        self.date_tree = ttk.Treeview(
            self.date_tab,
            columns=("Name", "Roll", "Time", "Confidence"),
            show="headings", height=15
        )
        for col, w in [("Name", 200), ("Roll", 120), ("Time", 120), ("Confidence", 120)]:
            self.date_tree.heading(col, text=col)
            self.date_tree.column(col, width=w)
        self.date_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _search_by_date(self):
        query_date = self.date_entry.get().strip()
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)
        try:
            conn = self.database.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.name, s.roll_number, a.time, a.confidence_score
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ?
                ORDER BY a.time DESC
            ''', (query_date,))
            rows = cursor.fetchall()
            conn.close()
            for name, roll, time, conf in rows:
                conf_str = f"{conf:.0%}" if conf else "N/A"
                self.date_tree.insert("", "end", values=(name, roll, str(time)[:8], conf_str))
            self.date_count_lbl.config(text=f"{len(rows)} student(s) present")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------ Tab 2
    def _create_student_tab(self):
        ctrl = tk.Frame(self.student_tab)
        ctrl.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(ctrl, text="Select Student:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(ctrl, textvariable=self.student_var, width=25, font=("Arial", 11))
        self.student_combo.pack(side=tk.LEFT, padx=10)

        tk.Button(
            ctrl, text="View History",
            command=self._search_by_student,
            bg="#3b82f6", fg="white", font=("Arial", 11), padx=10
        ).pack(side=tk.LEFT)

        self.student_count_lbl = tk.Label(ctrl, text="", font=("Arial", 11, "bold"), fg="#1e3a8a")
        self.student_count_lbl.pack(side=tk.LEFT, padx=20)

        self.student_tree = ttk.Treeview(
            self.student_tab,
            columns=("Date", "Time", "Confidence"),
            show="headings", height=15
        )
        for col, w in [("Date", 200), ("Time", 200), ("Confidence", 200)]:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=w)
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._load_students()

    def _load_students(self):
        conn = self.database.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT student_id, name, roll_number FROM students ORDER BY name')
        self._students = cursor.fetchall()
        conn.close()
        self.student_combo['values'] = [f"{name} (Roll: {roll})" for _, name, roll in self._students]

    def _search_by_student(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        idx = self.student_combo.current()
        if idx < 0:
            messagebox.showwarning("Select Student", "Please select a student.")
            return
        student_id = self._students[idx][0]
        conn = self.database.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, time, confidence_score FROM attendance
            WHERE student_id = ? ORDER BY date DESC, time DESC
        ''', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        for d, t, conf in rows:
            conf_str = f"{conf:.0%}" if conf else "N/A"
            self.student_tree.insert("", "end", values=(d, str(t)[:8], conf_str))
        self.student_count_lbl.config(text=f"{len(rows)} day(s) attended")

    # ------------------------------------------------------------------ Tab 3
    def _create_summary_tab(self):
        self.summary_tree = ttk.Treeview(
            self.summary_tab,
            columns=("Name", "Roll", "Days Present", "Attendance %"),
            show="headings", height=18
        )
        for col, w in [("Name", 220), ("Roll", 120), ("Days Present", 150), ("Attendance %", 150)]:
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=w)
        self.summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.summary_tree.tag_configure("low", background="#fee2e2", foreground="#dc2626")

        tk.Button(
            self.summary_tab, text="Refresh Summary",
            command=self._load_summary,
            bg="#3b82f6", fg="white", font=("Arial", 11), padx=15, pady=5
        ).pack(pady=5)

    def _load_summary(self):
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        try:
            conn = self.database.create_connection()
            cursor = conn.cursor()
            # Total unique days attendance was taken
            cursor.execute('SELECT COUNT(DISTINCT date) FROM attendance')
            total_days = cursor.fetchone()[0] or 1

            cursor.execute('''
                SELECT s.name, s.roll_number, COUNT(a.attendance_id) as days_present
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                ORDER BY days_present DESC
            ''')
            rows = cursor.fetchall()
            conn.close()
            for name, roll, days in rows:
                pct = f"{(days / total_days * 100):.1f}%"
                tag = "low" if (days / total_days * 100) < 75 else ""
                self.summary_tree.insert("", "end", values=(name, roll, days, pct), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", str(e))