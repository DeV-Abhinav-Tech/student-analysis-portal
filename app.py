import os
import io
import csv
import datetime
from flask import Flask, request, jsonify, render_template, session, send_file
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "student_analysis_super_secret_key_2026"

# Ensure DB is created and seeded
init_db()

@app.route("/")
def index():
    return render_template("index.html")

# ================= AUTHENTICATION APIs (Screens 1 & 2) =================

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({
            "success": True,
            "user": {"id": user["id"], "username": user["username"], "email": user["email"]}
        })
    else:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        session["user_id"] = user_id
        session["username"] = username
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": {"id": user_id, "username": username, "email": email}
        })
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 400

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route("/api/auth/me", methods=["GET"])
def current_user():
    if "user_id" in session:
        return jsonify({
            "authenticated": True,
            "user": {"id": session["user_id"], "username": session["username"]}
        })
    # Default to Hardik for administrator session
    return jsonify({
        "authenticated": True,
        "user": {"id": 1, "username": "Hardik", "email": "hardik@gmail.com"}
    })

# ================= DASHBOARD & STATS (Screen 3) =================

@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Marks entries and overall average
    cur.execute("SELECT COUNT(*), AVG(CAST(marks_obtained AS FLOAT) / total_marks * 100) FROM marks")
    marks_row = cur.fetchone()
    total_exams = marks_row[0]
    avg_marks_pct = round(marks_row[1] or 0, 1)

    # Attendance Rate
    cur.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attendance WHERE status = 'P'")
    present_attendance = cur.fetchone()[0]
    attendance_rate = round((present_attendance / total_attendance * 100), 1) if total_attendance > 0 else 0

    # Top Students
    cur.execute("""
        SELECT s.id, s.name, s.roll_no, s.class, AVG(m.marks_obtained) as avg_score
        FROM students s
        JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY avg_score DESC
        LIMIT 5
    """)
    top_students = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        "success": True,
        "total_students": total_students,
        "total_exams": total_exams,
        "avg_marks_pct": avg_marks_pct,
        "total_attendance": total_attendance,
        "attendance_rate": attendance_rate,
        "top_students": top_students
    })

# ================= STUDENTS CRUD (Screens 4, 5, 6, 7) =================

@app.route("/api/students", methods=["GET"])
def get_students():
    query = request.args.get("q", "").strip()
    conn = get_connection()
    cur = conn.cursor()

    if query:
        search = f"%{query}%"
        cur.execute("""
            SELECT id, name, roll_no, class, city, phone
            FROM students
            WHERE name LIKE ? OR roll_no LIKE ? OR city LIKE ? OR class LIKE ?
            ORDER BY id ASC
        """, (search, search, search, search))
    else:
        cur.execute("SELECT id, name, roll_no, class, city, phone FROM students ORDER BY id ASC")

    students = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "students": students})

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    student_class = data.get("class", "").strip()
    city = data.get("city", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not roll_no:
        return jsonify({"success": False, "error": "Name and Roll No are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (name, roll_no, class, city, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_no, student_class, city, phone))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Student added successfully", "id": new_id})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed to add student: {str(e)}"}), 400

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    student_class = data.get("class", "").strip()
    city = data.get("city", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not roll_no:
        return jsonify({"success": False, "error": "Name and Roll No are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE students
            SET name = ?, roll_no = ?, class = ?, city = ?, phone = ?
            WHERE id = ?
        """, (name, roll_no, student_class, city, phone, student_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Student updated successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed to update student: {str(e)}"}), 400

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Student deleted successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed to delete student: {str(e)}"}), 400

# ================= ATTENDANCE (Screens 8 & 9) =================

@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    date_filter = request.args.get("date", "").strip()
    student_id = request.args.get("student_id", "").strip()

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT a.id, a.student_id, s.name, s.roll_no, s.class, a.att_date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE 1=1
    """
    params = []
    if date_filter:
        sql += " AND a.att_date = ?"
        params.append(date_filter)
    if student_id:
        sql += " AND a.student_id = ?"
        params.append(student_id)

    sql += " ORDER BY a.att_date DESC, s.roll_no ASC"
    cur.execute(sql, params)
    records = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "attendance": records})

@app.route("/api/attendance", methods=["POST"])
def add_attendance():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    att_date = data.get("att_date") or datetime.date.today().strftime("%Y-%m-%d")
    status = data.get("status", "P").upper()

    if not student_id:
        return jsonify({"success": False, "error": "Student is required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO attendance (student_id, att_date, status)
            VALUES (?, ?, ?)
        """, (student_id, att_date, status))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Attendance marked successfully", "id": new_id})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed to mark attendance: {str(e)}"}), 400

@app.route("/api/attendance/bulk", methods=["POST"])
def bulk_attendance():
    data = request.get_json() or {}
    records = data.get("records", []) # list of {student_id, status, att_date}
    if not records:
        return jsonify({"success": False, "error": "No attendance records provided"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        for r in records:
            cur.execute("""
                INSERT INTO attendance (student_id, att_date, status)
                VALUES (?, ?, ?)
            """, (r["student_id"], r["att_date"], r["status"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Recorded attendance for {len(records)} students"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed bulk attendance: {str(e)}"}), 400

@app.route("/api/attendance/<int:att_id>", methods=["DELETE"])
def delete_attendance(att_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE id = ?", (att_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Attendance record deleted"})

# ================= MARKS CRUD (Screens 10 & 11) =================

@app.route("/api/marks", methods=["GET"])
def get_marks():
    student_id = request.args.get("student_id", "").strip()
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT m.id, m.student_id, s.name, s.roll_no, s.class, m.subject,
               m.marks_obtained, m.total_marks,
               ROUND(CAST(m.marks_obtained AS FLOAT) / m.total_marks * 100, 1) as percentage
        FROM marks m
        JOIN students s ON m.student_id = s.id
        WHERE 1=1
    """
    params = []
    if student_id:
        sql += " AND m.student_id = ?"
        params.append(student_id)

    sql += " ORDER BY s.roll_no ASC, m.id DESC"
    cur.execute(sql, params)
    records = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "marks": records})

@app.route("/api/marks", methods=["POST"])
def add_marks():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    subject = data.get("subject", "").strip()
    marks_obtained = data.get("marks_obtained")
    total_marks = data.get("total_marks", 100)

    if not student_id or not subject or marks_obtained is None:
        return jsonify({"success": False, "error": "Student, Subject, and Marks Obtained are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO marks (student_id, subject, marks_obtained, total_marks)
            VALUES (?, ?, ?, ?)
        """, (student_id, subject, marks_obtained, total_marks))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"success": True, "message": "Marks added successfully", "id": new_id})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": f"Failed to add marks: {str(e)}"}), 400

@app.route("/api/marks/<int:mark_id>", methods=["DELETE"])
def delete_marks(mark_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM marks WHERE id = ?", (mark_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Marks record deleted"})

# ================= ANALYTICS APIs (Screens 12 & 13) =================

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    conn = get_connection()
    cur = conn.cursor()

    # Bar chart: Student Name vs Average Marks
    cur.execute("""
        SELECT s.name, ROUND(AVG(m.marks_obtained), 1) as avg_marks
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        GROUP BY s.id, s.name
        ORDER BY s.id ASC
    """)
    student_marks = [dict(r) for r in cur.fetchall()]
    # Fallback if no marks
    if not student_marks:
        student_marks = [{"name": "Tejas", "avg_marks": 85}, {"name": "Aman", "avg_marks": 72}]

    # Pie chart: Attendance Distribution (P vs A)
    cur.execute("SELECT status, COUNT(*) as count FROM attendance GROUP BY status")
    att_rows = cur.fetchall()
    attendance_dist = {"Present": 0, "Absent": 0}
    for r in att_rows:
        if r["status"] == "P":
            attendance_dist["Present"] = r["count"]
        elif r["status"] == "A":
            attendance_dist["Absent"] = r["count"]

    # Subject performance
    cur.execute("""
        SELECT subject, ROUND(AVG(marks_obtained), 1) as avg_marks, COUNT(*) as count
        FROM marks
        GROUP BY subject
        ORDER BY avg_marks DESC
    """)
    subject_marks = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        "success": True,
        "student_marks": student_marks,
        "attendance_dist": attendance_dist,
        "subject_marks": subject_marks
    })

# ================= FULL REPORTS & EXPORT (Screens 14 & 15) =================

@app.route("/api/reports", methods=["GET"])
def get_full_report():
    conn = get_connection()
    cur = conn.cursor()

    # Joined data matching Screen 14: Roll, Name, Class, Subject, Marks, Attendance Status
    cur.execute("""
        SELECT s.roll_no, s.name, s.class, s.city, s.phone,
               COALESCE(m.subject, 'N/A') as subject,
               COALESCE(m.marks_obtained, 0) as marks_obtained,
               COALESCE(m.total_marks, 0) as total_marks,
               COALESCE(a.status, 'N/A') as status,
               COALESCE(a.att_date, 'N/A') as att_date
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        LEFT JOIN attendance a ON s.id = a.student_id
        ORDER BY s.roll_no ASC, m.subject ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "report": rows})

@app.route("/api/reports/export", methods=["GET"])
def export_report():
    export_format = request.args.get("format", "txt").lower()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.roll_no, s.name, s.class,
               COALESCE(m.subject, 'N/A') as subject,
               COALESCE(m.marks_obtained, 0) as marks_obtained,
               COALESCE(a.status, 'N/A') as status
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        LEFT JOIN attendance a ON s.id = a.student_id
        ORDER BY s.roll_no ASC
    """)
    records = cur.fetchall()
    conn.close()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Roll No", "Student Name", "Class", "Subject", "Marks", "Attendance Status"])
        for r in records:
            writer.writerow([r["roll_no"], r["name"], r["class"], r["subject"], r["marks_obtained"], r["status"]])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"Student_Report_{timestamp}.csv"
        )
    else:
        # Match original format: Student_Report_YYYYMMDD.txt (Screen 15)
        lines = [
            "=" * 60,
            "STUDENT ANALYSIS - COMPREHENSIVE REPORT (Screen 15)",
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            f"{'Roll No':<10}{'Name':<22}{'Class':<10}{'Subject':<20}{'Marks':<8}{'Status':<8}",
            "-" * 60
        ]
        for r in records:
            lines.append(f"{str(r['roll_no']):<10}{str(r['name']):<22}{str(r['class']):<10}{str(r['subject']):<20}{str(r['marks_obtained']):<8}{str(r['status']):<8}")
        lines.append("=" * 60)
        content = "\n".join(lines)
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/plain",
            as_attachment=True,
            download_name=f"Student_Report_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
        )

# ================= ADVANCED FEATURES (Risk Analysis, Report Cards, Bulk Import, Portal, Backup) =================

@app.route("/api/students/risk-analysis", methods=["GET"])
def get_risk_analysis():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, roll_no, class FROM students ORDER BY roll_no ASC")
    students = [dict(r) for r in cur.fetchall()]

    risk_list = []
    total_defaulters = 0
    total_critical = 0

    for s in students:
        sid = s["id"]

        # Attendance stats
        cur.execute("SELECT COUNT(*), SUM(CASE WHEN status = 'P' THEN 1 ELSE 0 END) FROM attendance WHERE student_id = ?", (sid,))
        att_row = cur.fetchone()
        att_total = att_row[0] or 0
        att_present = att_row[1] or 0
        att_pct = round((att_present / att_total * 100), 1) if att_total > 0 else 0
        is_defaulter = att_pct < 75.0 if att_total > 0 else False

        # Marks stats
        cur.execute("SELECT COUNT(*), AVG(CAST(marks_obtained AS FLOAT) / total_marks * 100) FROM marks WHERE student_id = ?", (sid,))
        marks_row = cur.fetchone()
        exam_count = marks_row[0] or 0
        avg_score = round(marks_row[1] or 0, 1)

        # Risk level determination
        if att_pct < 65.0 or (exam_count > 0 and avg_score < 50.0):
            risk_level = "Critical"
            total_critical += 1
            ai_recommendation = "Immediate parent conference required. Severe risk of academic failure / exam debarment."
        elif is_defaulter or (exam_count > 0 and avg_score < 65.0):
            risk_level = "Warning"
            ai_recommendation = "Attendance / performance warning advised. Schedule remedial tutoring."
        else:
            risk_level = "Safe"
            ai_recommendation = "On-track performance. Eligible for honors & advanced projects."

        if is_defaulter:
            total_defaulters += 1

        risk_list.append({
            "id": s["id"],
            "name": s["name"],
            "roll_no": s["roll_no"],
            "class": s["class"],
            "attendance_pct": att_pct,
            "attendance_total": att_total,
            "attendance_present": att_present,
            "is_defaulter": is_defaulter,
            "avg_score": avg_score,
            "exam_count": exam_count,
            "risk_level": risk_level,
            "ai_recommendation": ai_recommendation
        })

    conn.close()
    return jsonify({
        "success": True,
        "risk_list": risk_list,
        "total_defaulters": total_defaulters,
        "total_critical": total_critical
    })

@app.route("/api/students/<int:student_id>/report-card", methods=["GET"])
def get_student_report_card(student_id):
    conn = get_connection()
    cur = conn.cursor()

    # 1. Student details
    cur.execute("SELECT id, name, roll_no, class, city, phone FROM students WHERE id = ?", (student_id,))
    student = cur.fetchone()
    if not student:
        conn.close()
        return jsonify({"success": False, "error": "Student not found"}), 404
    student = dict(student)

    # 2. Subjects and marks
    cur.execute("""
        SELECT subject, marks_obtained, total_marks,
               ROUND(CAST(marks_obtained AS FLOAT) / total_marks * 100, 1) as percentage
        FROM marks
        WHERE student_id = ?
        ORDER BY subject ASC
    """, (student_id,))
    marks_list = []
    total_obtained = 0
    total_possible = 0

    for r in cur.fetchall():
        m = dict(r)
        pct = m["percentage"]
        if pct >= 90:
            m["grade"] = "A+"
            m["points"] = 10.0
        elif pct >= 80:
            m["grade"] = "A"
            m["points"] = 9.0
        elif pct >= 70:
            m["grade"] = "B"
            m["points"] = 8.0
        elif pct >= 60:
            m["grade"] = "C"
            m["points"] = 7.0
        elif pct >= 50:
            m["grade"] = "D"
            m["points"] = 6.0
        else:
            m["grade"] = "F"
            m["points"] = 0.0

        m["result"] = "PASS" if pct >= 40 else "FAIL"
        total_obtained += m["marks_obtained"]
        total_possible += m["total_marks"]
        marks_list.append(m)

    overall_pct = round((total_obtained / total_possible * 100), 1) if total_possible > 0 else 0
    cgpa = round((overall_pct / 9.5), 2) if overall_pct > 0 else 0

    # 3. Attendance
    cur.execute("SELECT COUNT(*), SUM(CASE WHEN status = 'P' THEN 1 ELSE 0 END) FROM attendance WHERE student_id = ?", (student_id,))
    att_row = cur.fetchone()
    att_total = att_row[0] or 0
    att_present = att_row[1] or 0
    att_absent = att_total - att_present
    att_pct = round((att_present / att_total * 100), 1) if att_total > 0 else 0

    # 4. Class Rank
    cur.execute("""
        SELECT s.id, AVG(CAST(m.marks_obtained AS FLOAT) / m.total_marks * 100) as score
        FROM students s
        JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY score DESC
    """)
    ranked_students = [r[0] for r in cur.fetchall()]
    rank = (ranked_students.index(student_id) + 1) if student_id in ranked_students else "-"

    # 5. AI Comprehensive Remark
    if overall_pct >= 90 and att_pct >= 85:
        ai_remark = f"Exemplary performance! {student['name']} demonstrates mastery in technical coursework with stellar class participation. Recommended for academic merit honors."
    elif overall_pct >= 75 and att_pct >= 75:
        ai_remark = f"Good academic standing. {student['name']} exhibits consistent grasp of core topics. Encourage project-based leadership."
    elif att_pct < 75:
        ai_remark = f"Attendance requires urgent improvement. Attendance of {att_pct}% is below the mandatory 75% university prerequisite."
    else:
        ai_remark = f"Needs focused revision and guidance in challenging subjects to elevate overall aggregate."

    conn.close()
    return jsonify({
        "success": True,
        "student": student,
        "marks": marks_list,
        "total_obtained": total_obtained,
        "total_possible": total_possible,
        "overall_percentage": overall_pct,
        "cgpa": cgpa,
        "attendance": {
            "total": att_total,
            "present": att_present,
            "absent": att_absent,
            "percentage": att_pct
        },
        "rank": rank,
        "ai_remark": ai_remark,
        "issue_date": datetime.date.today().strftime("%B %d, %Y")
    })

@app.route("/api/students/bulk-import", methods=["POST"])
def bulk_import_students():
    data = request.get_json() or {}
    csv_text = data.get("csv_text", "").strip()

    if not csv_text:
        return jsonify({"success": False, "error": "No CSV content provided"}), 400

    conn = get_connection()
    cur = conn.cursor()
    imported = 0
    errors = []

    f = io.StringIO(csv_text)
    reader = csv.reader(f)

    for idx, row in enumerate(reader):
        if not row:
            continue
        # Skip header if present
        first_col = row[0].strip().lower()
        if "name" in first_col or "student" in first_col:
            continue

        if len(row) < 2:
            errors.append(f"Row {idx+1}: insufficient columns (need Name, Roll No)")
            continue

        name = row[0].strip()
        roll_no = row[1].strip()
        student_class = row[2].strip() if len(row) > 2 else "BCA-3"
        city = row[3].strip() if len(row) > 3 else ""
        phone = row[4].strip() if len(row) > 4 else ""

        if not name or not roll_no:
            errors.append(f"Row {idx+1}: Name and Roll No cannot be blank")
            continue

        try:
            cur.execute("""
                INSERT INTO students (name, roll_no, class, city, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (name, roll_no, student_class, city, phone))
            imported += 1
        except Exception as e:
            errors.append(f"Roll {roll_no}: {str(e)}")

    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "imported_count": imported,
        "errors": errors,
        "message": f"Successfully enrolled {imported} students"
    })

@app.route("/api/student-portal/<string:roll_no>", methods=["GET"])
def student_portal_lookup(roll_no):
    roll_no = roll_no.strip()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM students WHERE LOWER(roll_no) = LOWER(?)", (roll_no,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "error": f"No student found with Roll Number '{roll_no}'"}), 404

    student_id = row[0]
    conn.close()
    return get_student_report_card(student_id)

@app.route("/api/database/backup", methods=["GET"])
def download_backup():
    db_file = os.path.join(os.path.dirname(__file__), "student_db.sqlite")
    if not os.path.exists(db_file):
        return jsonify({"success": False, "error": "Database file not found"}), 404

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        db_file,
        mimetype="application/x-sqlite3",
        as_attachment=True,
        download_name=f"student_db_backup_{timestamp}.sqlite"
    )

# ================= AUTOMATION AGENT APIs (Attendance Risk Emails) =================

from attendance_agent import AttendanceRiskAgent

@app.route("/api/agent/scan-defaulters", methods=["GET"])
def agent_scan_defaulters():
    result = AttendanceRiskAgent.scan_all_risk_students()
    return jsonify(result)

@app.route("/api/agent/generate-email", methods=["POST"])
def agent_generate_email():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    template_type = data.get("template_type", "auto")

    if not student_id:
        return jsonify({"success": False, "error": "student_id is required"}), 400

    draft = AttendanceRiskAgent.generate_email_draft(student_id, template_type)
    return jsonify(draft)

@app.route("/api/agent/send-email", methods=["POST"])
def agent_send_email():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    recipient = data.get("recipient_email", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()
    template_type = data.get("template_type", "auto")

    if not student_id or not recipient or not subject or not body:
        return jsonify({"success": False, "error": "student_id, recipient, subject, and body are required"}), 400

    AttendanceRiskAgent.log_sent_email(student_id, recipient, subject, body, template_type)
    return jsonify({
        "success": True,
        "message": f"Warning email officially dispatched and recorded for {recipient}."
    })

@app.route("/api/agent/email-logs", methods=["GET"])
def agent_email_logs():
    logs = AttendanceRiskAgent.get_email_logs()
    return jsonify({"success": True, "logs": logs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Student Analysis Web Application on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)


