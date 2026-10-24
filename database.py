import sqlite3
import os
import shutil
import datetime

# Determine database path (handle Vercel / serverless environment with writable /tmp)
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
if IS_VERCEL:
    TMP_DIR = "/tmp"
    DB_PATH = os.path.join(TMP_DIR, "student_db.sqlite")
    SRC_DB = os.path.join(os.path.dirname(__file__), "student_db.sqlite")
    if not os.path.exists(DB_PATH) and os.path.exists(SRC_DB):
        try:
            shutil.copyfile(SRC_DB, DB_PATH)
        except Exception as e:
            print("Notice: copy DB to /tmp failed, will initialize fresh:", e)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "student_db.sqlite")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT
    );
    """)
    
    # 2. Students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        class TEXT,
        city TEXT,
        phone TEXT
    );
    """)
    
    # 3. Attendance table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        att_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)
    
    # 4. Marks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        marks_obtained INTEGER NOT NULL,
        total_marks INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # 5. Email Logs table for AI Attendance Warning Agent
    cur.execute("""
    CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        recipient_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        template_type TEXT NOT NULL,
        status TEXT NOT NULL,
        sent_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # Ensure email column exists in students table
    try:
        cur.execute("ALTER TABLE students ADD COLUMN email TEXT")
    except Exception:
        pass # Column already exists
    
    # Populate default emails if null
    try:
        cur.execute("UPDATE students SET email = LOWER(REPLACE(name, ' ', '.')) || '@student.edu' WHERE email IS NULL OR email = ''")
    except Exception:
        pass
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (id, username, password, email) VALUES (1, 'Hardik', 'Hardik', 'hardik@gmail.com')")
        cur.execute("INSERT INTO users (username, password, email) VALUES ('admin', 'admin123', 'admin@studentanalysis.edu')")
    
    # Check if students table is populated
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        # Initial dump data from student_db.sql
        students_data = [
            (1, "Tejas Patiala", "101", "BCA-3", "Patiala", "9876543210"),
            (2, "Aman Ambala", "102", "BCA-3", "Ambala", "9876543211"),
            (3, "Priya Sharma", "103", "BCA-3", "Chandigarh", "9876543212"),
            (4, "Rahul Verma", "104", "BCA-3", "Ludhiana", "9876543213"),
            (5, "Simran Kaur", "105", "BCA-3", "Mohali", "9876543214"),
            (6, "Karan Singh", "106", "BCA-3", "Jalandhar", "9876543215")
        ]
        cur.executemany("INSERT INTO students (id, name, roll_no, class, city, phone) VALUES (?, ?, ?, ?, ?, ?)", students_data)
        
        # Initial marks data for rich analysis
        marks_data = [
            # Tejas
            (1, "Database Systems", 88, 100),
            (1, "Python Programming", 92, 100),
            (1, "Web Development", 85, 100),
            (1, "Data Structures", 81, 100),
            # Aman
            (2, "Database Systems", 72, 100),
            (2, "Python Programming", 75, 100),
            (2, "Web Development", 68, 100),
            (2, "Data Structures", 70, 100),
            # Priya
            (3, "Database Systems", 95, 100),
            (3, "Python Programming", 98, 100),
            (3, "Web Development", 94, 100),
            (3, "Data Structures", 96, 100),
            # Rahul
            (4, "Database Systems", 65, 100),
            (4, "Python Programming", 60, 100),
            (4, "Web Development", 70, 100),
            (4, "Data Structures", 64, 100),
            # Simran
            (5, "Database Systems", 84, 100),
            (5, "Python Programming", 89, 100),
            (5, "Web Development", 86, 100),
            (5, "Data Structures", 82, 100),
            # Karan
            (6, "Database Systems", 78, 100),
            (6, "Python Programming", 82, 100),
            (6, "Web Development", 79, 100),
            (6, "Data Structures", 75, 100)
        ]
        cur.executemany("INSERT INTO marks (student_id, subject, marks_obtained, total_marks) VALUES (?, ?, ?, ?)", marks_data)
        
        # Initial attendance records
        today = datetime.date.today()
        attendance_data = []
        for d_offset in range(10, -1, -1):
            att_date = (today - datetime.timedelta(days=d_offset)).strftime("%Y-%m-%d")
            # Create realistic attendance status
            attendance_data.append((1, att_date, "P"))
            attendance_data.append((2, att_date, "A" if d_offset in (2, 7) else "P"))
            attendance_data.append((3, att_date, "P"))
            attendance_data.append((4, att_date, "A" if d_offset in (1, 4, 8) else "P"))
            attendance_data.append((5, att_date, "P" if d_offset != 3 else "A"))
            attendance_data.append((6, att_date, "P" if d_offset != 5 else "A"))
            
        cur.executemany("INSERT INTO attendance (student_id, att_date, status) VALUES (?, ?, ?)", attendance_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
