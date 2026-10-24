import datetime
import urllib.parse
from database import get_connection

class AttendanceRiskAgent:
    """
    Automated Intelligence Agent that detects student attendance risk (<75%),
    evaluates historical absence patterns, and drafts personalized formal
    advisory, warning, and parent intervention emails.
    """

    MANDATORY_THRESHOLD = 75.0
    CRITICAL_THRESHOLD = 65.0

    @classmethod
    def evaluate_student_attendance(cls, student_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, name, roll_no, class, city, phone, email FROM students WHERE id = ?", (student_id,))
        student = cur.fetchone()
        if not student:
            conn.close()
            return None
        student = dict(student)
        if not student.get("email"):
            student["email"] = f"{student['name'].lower().replace(' ', '.')}@student.edu"

        # Attendance stats
        cur.execute("SELECT att_date, status FROM attendance WHERE student_id = ? ORDER BY att_date DESC", (student_id,))
        records = [dict(r) for r in cur.fetchall()]
        conn.close()

        total_days = len(records)
        present_days = sum(1 for r in records if r["status"] == "P")
        absent_days = total_days - present_days
        att_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0

        is_defaulter = att_pct < cls.MANDATORY_THRESHOLD if total_days > 0 else False
        is_critical = att_pct < cls.CRITICAL_THRESHOLD if total_days > 0 else False
        shortfall_pct = round(cls.MANDATORY_THRESHOLD - att_pct, 1) if is_defaulter else 0.0

        # Recent absences
        recent_absences = [r["att_date"] for r in records if r["status"] == "A"][:5]

        return {
            "student": student,
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "att_pct": att_pct,
            "is_defaulter": is_defaulter,
            "is_critical": is_critical,
            "shortfall_pct": shortfall_pct,
            "recent_absences": recent_absences
        }

    @classmethod
    def generate_email_draft(cls, student_id, template_type="auto"):
        eval_data = cls.evaluate_student_attendance(student_id)
        if not eval_data:
            return {"success": False, "error": "Student record not found"}

        student = eval_data["student"]
        att_pct = eval_data["att_pct"]
        total_days = eval_data["total_days"]
        present_days = eval_data["present_days"]
        absent_days = eval_data["absent_days"]
        shortfall_pct = eval_data["shortfall_pct"]
        recent_absences = eval_data["recent_absences"]
        absent_str = ", ".join(recent_absences) if recent_absences else "Recent lectures"

        # Auto-detect appropriate template if 'auto'
        if template_type == "auto":
            if eval_data["is_critical"]:
                template_type = "critical_debarment"
            elif eval_data["is_defaulter"]:
                template_type = "first_warning"
            else:
                template_type = "advisory"

        today_str = datetime.date.today().strftime("%B %d, %Y")

        if template_type == "critical_debarment":
            subject = f"[CRITICAL NOTICE] Examination Debarment Warning: Severe Attendance Deficit - {student['name']} (Roll: {student['roll_no']})"
            urgency = "CRITICAL"
            action_required = "Immediate appearance before the Department Head and Academic Disciplinary Committee."
            consequence = "Pursuant to University Academic Regulation 14.2, students maintaining below 65% aggregate attendance shall be summarily debarred from sitting for the upcoming Semester Examinations."
        elif template_type == "parent_meeting":
            subject = f"Official Notice: Parent-Faculty Attendance Conference Request for {student['name']} (Roll: {student['roll_no']})"
            urgency = "HIGH"
            action_required = "Parent / Guardian presence required for academic counseling within 3 working days."
            consequence = "Failure to address recurring absenteeism may jeopardize your ward's course registration and exam eligibility."
        elif template_type == "first_warning":
            subject = f"[ACTION REQUIRED] Official Attendance Warning Notice: {student['name']} (Roll: {student['roll_no']})"
            urgency = "WARNING"
            action_required = "Ensure 100% attendance in all scheduled classes over the next 14 days to recover aggregate."
            consequence = "Failure to attain the statutory 75.0% threshold prior to hall ticket issuance will result in debarment from practical and theory exams."
        else: # Advisory / Safe
            subject = f"Academic Attendance Update & Progress Notification - {student['name']} (Roll: {student['roll_no']})"
            urgency = "INFORMATIONAL"
            action_required = "Maintain consistent attendance throughout the semester."
            consequence = "Compliance with the 75% university benchmark ensures honors eligibility."

        # Plain text email body
        body_text = f"""Dear {student['name']},

This is an automated academic communication from the Department of Computer Applications regarding your attendance record for the current semester ({student.get('class', 'BCA-3')}).

STUDENT ATTENDANCE AUDIT:
--------------------------------------------------
• Student Name: {student['name']}
• Roll Number: {student['roll_no']}
• Class / Batch: {student.get('class', 'BCA-3')}
• Lectures Conducted: {total_days} days
• Lectures Attended: {present_days} days
• Total Absent Days: {absent_days} days
• Current Attendance Rate: {att_pct}% (Mandatory Prerequisite: 75.0%)
• Deficit / Shortfall: {shortfall_pct}% below required benchmark
• Recent Unexcused Absences: {absent_str}
--------------------------------------------------

ACADEMIC DIRECTIVE & CONSEQUENCE:
{consequence}

MANDATORY NEXT STEPS:
1. {action_required}
2. Submit medical or authorized leave documentation (if applicable) to the Department Office.
3. Schedule an advisement session with your Class Coordinator.

Date of Notice: {today_str}
Office of the Academic Dean & Attendance Monitoring Cell
Department of Computer Applications
National Institute of Academic Sciences
Contact: attendance-cell@nias.edu.in | +91 175-2345678
"""

        # HTML Email Body (Beautiful styled template)
        body_html = f"""
        <div style="font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif; max-width:620px; margin:0 auto; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.06); color:#1e293b;">
          <div style="background:{'#dc2626' if urgency == 'CRITICAL' else ('#d97706' if urgency == 'WARNING' else '#2563eb')}; color:#ffffff; padding:24px 28px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; opacity:0.85; font-weight:700;">Department of Computer Applications • Attendance Cell</div>
            <h2 style="margin:6px 0 0; font-size:20px; font-weight:700;">{subject}</h2>
          </div>
          <div style="padding:28px;">
            <p style="font-size:15px; line-height:1.6; margin-top:0;">Dear <strong>{student['name']}</strong>,</p>
            <p style="font-size:14px; color:#475569; line-height:1.6;">An automated attendance audit conducted on <strong>{today_str}</strong> has flagged your profile due to non-compliance with the statutory <strong>75% attendance criterion</strong>.</p>
            
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:18px 20px; margin:20px 0;">
              <table style="width:100%; border-collapse:collapse; font-size:13.5px;">
                <tr>
                  <td style="padding:6px 0; color:#64748b;">Roll Number:</td>
                  <td style="padding:6px 0; font-weight:700; color:#0f172a; text-align:right;">{student['roll_no']}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0; color:#64748b;">Class / Section:</td>
                  <td style="padding:6px 0; font-weight:600; color:#0f172a; text-align:right;">{student.get('class', 'BCA-3')}</td>
                </tr>
                <tr>
                  <td style="padding:6px 0; color:#64748b;">Classes Attended:</td>
                  <td style="padding:6px 0; font-weight:600; color:#0f172a; text-align:right;">{present_days} of {total_days} Lectures</td>
                </tr>
                <tr>
                  <td style="padding:6px 0; color:#64748b;">Current Attendance Rate:</td>
                  <td style="padding:6px 0; font-weight:800; color:{'#dc2626' if att_pct < 65 else ('#d97706' if att_pct < 75 else '#16a34a')}; text-align:right; font-size:16px;">
                    {att_pct}% <span style="font-size:11px; font-weight:600; padding:2px 6px; border-radius:4px; background:{'#fee2e2; color:#b91c1c;' if att_pct < 75 else '#dcfce7; color:#15803d;'}">{'DEFAULTER' if att_pct < 75 else 'COMPLIANT'}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:6px 0; color:#64748b;">Required Threshold:</td>
                  <td style="padding:6px 0; font-weight:700; color:#0f172a; text-align:right;">75.0%</td>
                </tr>
              </table>
            </div>

            <div style="background:#fef2f2; border-left:4px solid #ef4444; padding:14px 16px; border-radius:4px; margin-bottom:20px;">
              <strong style="color:#991b1b; font-size:13.5px; display:block; margin-bottom:4px;">Regulatory Consequence:</strong>
              <p style="margin:0; font-size:13px; color:#7f1d1d; line-height:1.5;">{consequence}</p>
            </div>

            <h4 style="margin:20px 0 8px; font-size:14px; color:#0f172a;">Required Action:</h4>
            <p style="margin:0; font-size:13.5px; color:#334155; line-height:1.6;">{action_required}</p>

            <div style="margin-top:28px; padding-top:18px; border-top:1px solid #e2e8f0; font-size:12px; color:#64748b; line-height:1.5;">
              <strong>Academic Monitoring Cell</strong><br>
              Department of Computer Applications • National Institute of Academic Sciences<br>
              Inquiries: <a href="mailto:attendance-cell@nias.edu.in" style="color:#2563eb;">attendance-cell@nias.edu.in</a>
            </div>
          </div>
        </div>
        """

        mailto_params = urllib.parse.urlencode({
            "subject": subject,
            "body": body_text
        })
        mailto_url = f"mailto:{student['email']}?{mailto_params}"

        return {
            "success": True,
            "student_id": student["id"],
            "student_name": student["name"],
            "student_email": student["email"],
            "roll_no": student["roll_no"],
            "attendance_pct": att_pct,
            "is_defaulter": eval_data["is_defaulter"],
            "is_critical": eval_data["is_critical"],
            "urgency": urgency,
            "template_type": template_type,
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
            "mailto_url": mailto_url
        }

    @classmethod
    def scan_all_risk_students(cls):
        """Scans all enrolled students and returns generated drafts for all attendance defaulters."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM students ORDER BY roll_no ASC")
        all_ids = [r[0] for r in cur.fetchall()]
        conn.close()

        drafts = []
        for sid in all_ids:
            eval_data = cls.evaluate_student_attendance(sid)
            if eval_data and eval_data["is_defaulter"]:
                draft = cls.generate_email_draft(sid, "auto")
                if draft.get("success"):
                    drafts.append(draft)

        return {
            "success": True,
            "total_defaulters_flagged": len(drafts),
            "generated_queue": drafts,
            "scanned_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def log_sent_email(cls, student_id, recipient, subject, body, template_type="auto"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO email_logs (student_id, recipient_email, subject, body, template_type, status, sent_at)
            VALUES (?, ?, ?, ?, ?, 'SENT', ?)
        """, (student_id, recipient, subject, body, template_type, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True

    @classmethod
    def get_email_logs(cls):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.id, l.student_id, s.name, s.roll_no, l.recipient_email, l.subject, l.template_type, l.status, l.sent_at
            FROM email_logs l
            JOIN students s ON l.student_id = s.id
            ORDER BY l.id DESC
            LIMIT 50
        """)
        logs = [dict(r) for r in cur.fetchall()]
        conn.close()
        return logs
