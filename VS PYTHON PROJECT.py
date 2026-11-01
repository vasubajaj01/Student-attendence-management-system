from datetime import datetime
import csv
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ProfessionalAttendanceApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Enterprise MCA Attendance Management System")
    self.root.geometry("1024x680")
    self.root.config(bg="#f8fafc")

    # Initialize Database & Pre-load 10 Sample Students
    self.init_db()

    # Styling Setup
    style = ttk.Style()
    style.theme_use("clam")

    # Configure Notebook Tabs
    style.configure(
        "TNotebook", background="#f8fafc", borderwidth=0, tabmargins=[4, 8, 4, 0]
    )
    style.configure(
        "TNotebook.Tab",
        font=("Segoe UI", 11, "bold"),
        padding=[20, 12],
        background="#e2e8f0",
        foreground="#475569",
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#2563eb")],
        foreground=[("selected", "#ffffff")],
    )

    # Configure Treeview
    style.configure(
        "Treeview",
        font=("Segoe UI", 10),
        rowheight=30,
        background="#ffffff",
        fieldbackground="#ffffff",
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        background="#e2e8f0",
        foreground="#1e293b",
        relief="flat",
    )
    style.map("Treeview", background=[("selected", "#dbeafe")])

    # Header Banner
    header = tk.Frame(root, bg="#0f172a", pady=18)
    header.pack(fill=tk.X)

    tk.Label(
        header,
        text="🎓 Master of Computer Applications (MCA)",
        font=("Segoe UI", 18, "bold"),
        bg="#0f172a",
        fg="#f8fafc",
    ).pack(side=tk.LEFT, padx=30)
    tk.Label(
        header,
        text="Attendance Intelligence Dashboard v2.0",
        font=("Segoe UI", 10),
        bg="#0f172a",
        fg="#94a3b8",
    ).pack(side=tk.RIGHT, padx=30)

    # Main Notebook Container
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    self.tab_dashboard = ttk.Frame(self.notebook)
    self.tab_students = ttk.Frame(self.notebook)
    self.tab_attendance = ttk.Frame(self.notebook)
    self.tab_reports = ttk.Frame(self.notebook)

    self.notebook.add(self.tab_dashboard, text=" 📊 Dashboard ")
    self.notebook.add(self.tab_students, text=" 👥 Manage Students ")
    self.notebook.add(self.tab_attendance, text=" 📝 Mark Attendance ")
    self.notebook.add(self.tab_reports, text=" 📈 Reports & Export ")

    self.setup_dashboard_tab()
    self.setup_students_tab()
    self.setup_attendance_tab()
    self.setup_reports_tab()

  def init_db(self):
    self.conn = sqlite3.connect("mca_enterprise_attendance.db")
    self.cursor = self.conn.cursor()

    # Create Tables
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                semester TEXT NOT NULL
            )
        """)
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT,
                date TEXT,
                status TEXT,
                FOREIGN KEY(roll_no) REFERENCES students(roll_no)
            )
        """)
    self.conn.commit()

    # Auto-seed 10 sample MCA students if table is empty
    self.cursor.execute("SELECT COUNT(*) FROM students")
    if self.cursor.fetchone()[0] == 0:
      sample_students = [
          ("MCA2026001", "Aarav Sharma", "Semester 1"),
          ("MCA2026002", "Priya Patel", "Semester 1"),
          ("MCA2026003", "Rohan Verma", "Semester 3"),
          ("MCA2026004", "Sneha Gupta", "Semester 3"),
          ("MCA2026005", "Vikram Singh", "Semester 5"),
          ("MCA2026006", "Ananya Iyer", "Semester 5"),
          ("MCA2026007", "Rahul Nair", "Semester 1"),
          ("MCA2026008", "Neha Reddy", "Semester 3"),
          ("MCA2026009", "Aditya Deshmukh", "Semester 5"),
          ("MCA2026010", "Pooja Kulkarni", "Semester 1"),
      ]
      self.cursor.executemany(
          "INSERT INTO students (roll_no, name, semester) VALUES (?, ?, ?)",
          sample_students,
      )
      self.conn.commit()

  # ----------------------------------------------------
  # 1. DASHBOARD TAB
  # ----------------------------------------------------
  def setup_dashboard_tab(self):
    frame = tk.Frame(self.tab_dashboard, bg="#f8fafc", padx=25, pady=25)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        frame,
        text="System Analytics Overview",
        font=("Segoe UI", 15, "bold"),
        bg="#f8fafc",
        fg="#1e293b",
    ).pack(anchor="w", pady=(0, 20))

    cards_frame = tk.Frame(frame, bg="#f8fafc")
    cards_frame.pack(fill=tk.X, pady=10)

    # Card 1: Total Students
    self.card_total = self.create_metric_card(
        cards_frame, "Total Registered Students", "0", "#2563eb"
    )
    self.card_total.pack(side=tk.LEFT, padx=(0, 20), expand=True, fill=tk.X)

    # Card 2: Today Present
    self.card_present = self.create_metric_card(
        cards_frame, "Marked Present Today", "0", "#16a34a"
    )
    self.card_present.pack(
        side=tk.LEFT, padx=(0, 20), expand=True, fill=tk.X
    )

    # Card 3: Today Absent
    self.card_absent = self.create_metric_card(
        cards_frame, "Marked Absent Today", "0", "#dc2626"
    )
    self.card_absent.pack(side=tk.LEFT, expand=True, fill=tk.X)

    btn_refresh_dash = tk.Button(
        frame,
        text="🔄 Refresh Analytics",
        command=self.update_dashboard_metrics,
        bg="#0284c7",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
    )
    btn_refresh_dash.pack(anchor="w", pady=30)

    self.update_dashboard_metrics()

  def create_metric_card(self, parent, title, value, accent_color):
    card = tk.Frame(
        parent, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1
    )
    inner = tk.Frame(card, bg="#ffffff", padx=20, pady=20)
    inner.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        inner,
        text=title,
        font=("Segoe UI", 10, "bold"),
        bg="#ffffff",
        fg="#64748b",
    ).pack(anchor="w")
    val_lbl = tk.Label(
        inner,
        text=value,
        font=("Segoe UI", 24, "bold"),
        bg="#ffffff",
        fg=accent_color,
    )
    val_lbl.pack(anchor="w", pady=(5, 0))
    card.val_lbl = val_lbl
    return card

  def update_dashboard_metrics(self):
    self.cursor.execute("SELECT COUNT(*) FROM students")
    total_students = self.cursor.fetchone()[0]

    today_str = datetime.now().strftime("%Y-%m-%d")
    self.cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'",
        (today_str,),
    )
    present_count = self.cursor.fetchone()[0]

    self.cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Absent'",
        (today_str,),
    )
    absent_count = self.cursor.fetchone()[0]

    self.card_total.val_lbl.config(text=str(total_students))
    self.card_present.val_lbl.config(text=str(present_count))
    self.card_absent.val_lbl.config(text=str(absent_count))

  # ----------------------------------------------------
  # 2. MANAGE STUDENTS TAB
  # ----------------------------------------------------
  def setup_students_tab(self):
    frame = tk.Frame(self.tab_students, bg="#f8fafc", padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    form_card = tk.Frame(
        frame,
        bg="#ffffff",
        padx=20,
        pady=20,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    form_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

    tk.Label(
        form_card,
        text="Student Registration",
        font=("Segoe UI", 12, "bold"),
        bg="#ffffff",
        fg="#1e293b",
    ).pack(anchor="w", pady=(0, 15))

    tk.Label(
        form_card,
        text="Roll Number / ID",
        font=("Segoe UI", 9, "bold"),
        bg="#ffffff",
        fg="#64748b",
    ).pack(anchor="w")
    self.roll_entry = tk.Entry(
        form_card, font=("Segoe UI", 11), bg="#f8fafc", relief="solid", bd=1
    )
    self.roll_entry.pack(fill=tk.X, pady=(4, 12), ipady=4)

    tk.Label(
        form_card,
        text="Full Name",
        font=("Segoe UI", 9, "bold"),
        bg="#ffffff",
        fg="#64748b",
    ).pack(anchor="w")
    self.name_entry = tk.Entry(
        form_card, font=("Segoe UI", 11), bg="#f8fafc", relief="solid", bd=1
    )
    self.name_entry.pack(fill=tk.X, pady=(4, 12), ipady=4)

    tk.Label(
        form_card,
        text="Semester",
        font=("Segoe UI", 9, "bold"),
        bg="#ffffff",
        fg="#64748b",
    ).pack(anchor="w")
    self.sem_combo = ttk.Combobox(
        form_card,
        values=[
            "Semester 1",
            "Semester 2",
            "Semester 3",
            "Semester 4",
            "Semester 5",
            "Semester 6",
        ],
        font=("Segoe UI", 11),
        state="readonly",
    )
    self.sem_combo.pack(fill=tk.X, pady=(4, 20), ipady=4)
    self.sem_combo.current(0)

    btn_add = tk.Button(
        form_card,
        text="Register Student",
        command=self.add_student,
        bg="#2563eb",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        pady=8,
    )
    btn_add.pack(fill=tk.X)

    table_card = tk.Frame(
        frame,
        bg="#ffffff",
        padx=15,
        pady=15,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    table_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(
        table_card,
        text="Registered Directory",
        font=("Segoe UI", 12, "bold"),
        bg="#ffffff",
        fg="#1e293b",
    ).pack(anchor="w", pady=(0, 10))

    self.student_tree = ttk.Treeview(
        table_card, columns=("Roll No", "Name", "Semester"), show="headings"
    )
    self.student_tree.heading("Roll No", text="Roll No")
    self.student_tree.heading("Name", text="Full Name")
    self.student_tree.heading("Semester", text="Semester")
    self.student_tree.pack(fill=tk.BOTH, expand=True)

    self.load_students()

  def add_student(self):
    roll = self.roll_entry.get().strip()
    name = self.name_entry.get().strip()
    sem = self.sem_combo.get().strip()

    if not roll or not name:
      messagebox.showerror(
          "Error", "Roll Number and Name cannot be left blank!"
      )
      return

    try:
      self.cursor.execute(
          "INSERT INTO students (roll_no, name, semester) VALUES (?, ?, ?)",
          (roll, name, sem),
      )
      self.conn.commit()
      messagebox.showinfo("Success", "Student registered successfully!")
      self.roll_entry.delete(0, tk.END)
      self.name_entry.delete(0, tk.END)
      self.load_students()
      self.load_attendance_students()
      self.update_dashboard_metrics()
    except sqlite3.IntegrityError:
      messagebox.showerror(
          "Error", "Student with this Roll Number already exists!"
      )

  def load_students(self):
    for row in self.student_tree.get_children():
      self.student_tree.delete(row)
    self.cursor.execute("SELECT * FROM students")
    for row in self.cursor.fetchall():
      self.student_tree.insert("", tk.END, values=row)

  # ----------------------------------------------------
  # 3. MARK ATTENDANCE TAB
  # ----------------------------------------------------
  def setup_attendance_tab(self):
    frame = tk.Frame(self.tab_attendance, bg="#f8fafc", padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    top_bar = tk.Frame(
        frame,
        bg="#ffffff",
        padx=15,
        pady=12,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    top_bar.pack(fill=tk.X, pady=(0, 15))

    tk.Label(
        top_bar,
        text="Attendance Date (YYYY-MM-DD):",
        font=("Segoe UI", 10, "bold"),
        bg="#ffffff",
        fg="#334155",
    ).pack(side=tk.LEFT, padx=(0, 10))
    self.date_entry = tk.Entry(
        top_bar, font=("Segoe UI", 11), width=15, relief="solid", bd=1
    )
    self.date_entry.pack(side=tk.LEFT, ipady=3)
    self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(
        top_bar,
        text="💡 Hold Ctrl/Shift to multi-select students",
        font=("Segoe UI", 9, "italic"),
        bg="#ffffff",
        fg="#64748b",
    ).pack(side=tk.RIGHT)

    table_card = tk.Frame(
        frame,
        bg="#ffffff",
        padx=15,
        pady=15,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    self.att_tree = ttk.Treeview(
        table_card, columns=("Roll No", "Name", "Status"), show="headings"
    )
    self.att_tree.heading("Roll No", text="Roll No")
    self.att_tree.heading("Name", text="Full Name")
    self.att_tree.heading("Status", text="Current Status")
    self.att_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    btn_panel = tk.Frame(table_card, bg="#ffffff")
    btn_panel.pack(fill=tk.X)

    tk.Button(
        btn_panel,
        text="✔ Mark Present",
        command=lambda: self.mark_status("Present"),
        bg="#16a34a",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=8,
    ).pack(side=tk.LEFT, padx=(0, 12))
    tk.Button(
        btn_panel,
        text="✖ Mark Absent",
        command=lambda: self.mark_status("Absent"),
        bg="#dc2626",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=8,
    ).pack(side=tk.LEFT)

    self.load_attendance_students()

  def load_attendance_students(self):
    for row in self.att_tree.get_children():
      self.att_tree.delete(row)
    self.cursor.execute("SELECT roll_no, name FROM students")
    for row in self.cursor.fetchall():
      self.att_tree.insert("", tk.END, values=(row[0], row[1], "Not Marked"))

  def mark_status(self, status):
    selected = self.att_tree.selection()
    if not selected:
      messagebox.showerror(
          "Error", "Please select student(s) from the table first!"
      )
      return

    date_str = self.date_entry.get().strip()
    if not date_str:
      messagebox.showerror("Error", "Date cannot be empty!")
      return

    for item in selected:
      vals = self.att_tree.item(item, "values")
      roll_no = vals[0]

      self.cursor.execute(
          "SELECT id FROM attendance WHERE roll_no = ? AND date = ?",
          (roll_no, date_str),
      )
      if self.cursor.fetchone():
        self.cursor.execute(
            "UPDATE attendance SET status = ? WHERE roll_no = ? AND date = ?",
            (status, roll_no, date_str),
        )
      else:
        self.cursor.execute(
            "INSERT INTO attendance (roll_no, date, status) VALUES (?, ?, ?)",
            (roll_no, date_str, status),
        )
      self.conn.commit()
      self.att_tree.item(item, values=(vals[0], vals[1], status))

    messagebox.showinfo("Success", f"Attendance marked as {status}!")
    self.update_dashboard_metrics()

  # ----------------------------------------------------
  # 4. REPORTS & EXPORT TAB
  # ----------------------------------------------------
  def setup_reports_tab(self):
    frame = tk.Frame(self.tab_reports, bg="#f8fafc", padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    top_bar = tk.Frame(
        frame,
        bg="#ffffff",
        padx=15,
        pady=12,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    top_bar.pack(fill=tk.X, pady=(0, 15))

    tk.Label(
        top_bar,
        text="Complete Attendance Logs",
        font=("Segoe UI", 12, "bold"),
        bg="#ffffff",
        fg="#1e293b",
    ).pack(side=tk.LEFT)

    btn_export = tk.Button(
        top_bar,
        text="📥 Export to CSV",
        command=self.export_csv,
        bg="#059669",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=12,
        pady=6,
    )
    btn_export.pack(side=tk.RIGHT, padx=(10, 0))

    btn_refresh = tk.Button(
        top_bar,
        text="🔄 Refresh Logs",
        command=self.load_reports,
        bg="#0284c7",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=12,
        pady=6,
    )
    btn_refresh.pack(side=tk.RIGHT)

    table_card = tk.Frame(
        frame,
        bg="#ffffff",
        padx=15,
        pady=15,
        highlightbackground="#cbd5e1",
        highlightthickness=1,
    )
    table_card.pack(fill=tk.BOTH, expand=True)

    self.report_tree = ttk.Treeview(
        table_card,
        columns=("Roll No", "Name", "Date", "Status"),
        show="headings",
    )
    self.report_tree.heading("Roll No", text="Roll No")
    self.report_tree.heading("Name", text="Student Name")
    self.report_tree.heading("Date", text="Date")
    self.report_tree.heading("Status", text="Status")

    # Configure color tags for Present / Absent
    self.report_tree.tag_configure("Present", foreground="#16a34a")
    self.report_tree.tag_configure("Absent", foreground="#dc2626")

    self.report_tree.pack(fill=tk.BOTH, expand=True)
    self.load_reports()

  def load_reports(self):
    for row in self.report_tree.get_children():
      self.report_tree.delete(row)

    query = """
            SELECT students.roll_no, students.name, attendance.date, attendance.status 
            FROM attendance 
            JOIN students ON students.roll_no = attendance.roll_no 
            ORDER BY attendance.date DESC
        """
    self.cursor.execute(query)
    for row in self.cursor.fetchall():
      status = row[3]
      self.report_tree.insert("", tk.END, values=row, tags=(status,))

  def export_csv(self):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Export Attendance Logs",
    )
    if not file_path:
      return

    try:
      with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Roll No", "Student Name", "Date", "Status"])
        query = """
                    SELECT students.roll_no, students.name, attendance.date, attendance.status 
                    FROM attendance 
                    JOIN students ON students.roll_no = attendance.roll_no 
                    ORDER BY attendance.date DESC
                """
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
          writer.writerow(row)
      messagebox.showinfo(
          "Success", "Attendance logs successfully exported to CSV!"
      )
    except Exception as e:
      messagebox.showerror("Error", f"Failed to export file: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = ProfessionalAttendanceApp(root)
  root.mainloop()