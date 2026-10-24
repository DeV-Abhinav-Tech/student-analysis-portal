# 🎓 Student Analysis & Intelligence Portal (Local Host)

A full-stack Academic Management, Performance Intelligence, and Analytics web portal built to host and extend the **Student Analysis System** with zero configuration.

---

## 🌐 Quick Access
- **Local Web App:** [http://localhost:5000](http://localhost:5000) (or [http://127.0.0.1:5000](http://127.0.0.1:5000))
- **Default Login:**
  - Username: `Hardik`
  - Password: `Hardik`
  - *(or register any new user in the Sign Up tab)*
- **One-Click Launch:** Run `start_server.bat` in this folder.

---

## ✨ Features & Implemented Modules

### 1. 🛡️ Early Warning & Academic Risk Radar
- **Attendance Defaulter Alerts:** Automatically detects and tags any student falling below the statutory **75% attendance criteria**.
- **Risk Classification:** Identifies students as **Safe**, **Warning**, or **Critical** based on composite evaluation of attendance history and exam failures.
- **AI Remedial Advice:** Generates personalized counseling and remedial tutoring recommendations for faculty advisors.
- **Simulate Parent Alerts:** Instant notification generation for parents regarding student attendance and risk status.

### 2. 📄 Official Printable Report Cards (PDF / Transcript)
- Accessible from the Student Directory (`📄` icon) or directly from the Student Portal.
- Formatted institutional grade sheet complete with:
  - University/College Header & Academic Session
  - Student Profile & Class Rank
  - Subject-wise Marks, Percentages, Letter Grades (A+, A, B, C, F), and Grade Points (10.0 scale)
  - Cumulative GPA (CGPA) and Total Aggregate %
  - Detailed Attendance Ledger (Lectures Held, Attended, Absent, %)
  - AI Advisor Remarks
  - Official Signatory Stamp Lines (Class Coordinator, Controller of Examinations, Principal)
  - One-click **Print / Save as PDF** (`window.print()`).

### 3. 🏆 Merit Certificate of Academic Excellence
- Accessible from the Student Directory (`🏆` icon).
- Classical ceremonial certificate of honor for top-ranking students with Gold Seal badge, distinction citation, and official verification signatures.

### 4. 📥 Bulk CSV Student Enrollment
- Upload or paste CSV rosters (`Name, Roll No, Class, City, Phone`) with automatic duplicate validation and batch insert.
- Includes a 1-click sample template generator.

### 5. 🔍 Student & Parent Self-Service Portal
- Public lookup module where students or parents enter their **Roll Number** (e.g. `101`, `102`, `103`...) to view their individual performance, marks breakdown, attendance record, class rank, and printable transcript without accessing administrative tools.

### 6. 💾 1-Click Database Backup (.sqlite)
- Direct backup download button in the sidebar footer to export a snapshot of the live SQLite database at any time.

### 7. 🤖 AI Attendance Risk Email Automation Agent (`Auto Bot`)
- **Autonomous Roster Scan:** The agent autonomously scans all student records and flags anyone falling below the mandatory **75% attendance threshold** or into critical **<65% debarment territory**.
- **Context-Aware Email Generator:** Dynamically drafts personalized, formal warning emails complete with:
  - Student name, roll number, class
  - Exact attendance rate, lectures attended vs held, and deficit shortfall
  - List of recent unexcused absences
  - University regulatory debarment warnings
  - Action items (counseling session, leave documentation)
- **Multi-Persona Templates:**
  - *First Attendance Warning* (70% - 74.9%)
  - *Final Debarment Notice* (< 65% Severe)
  - *Parent-Faculty Counseling Conference Request*
- **Dispatch Channels:**
  - Instant pre-filled `mailto:` client launch (Outlook, Mail, Thunderbird)
  - One-click text copying to clipboard
  - Internal audit logging in `email_logs` table with dispatch history tracker.

---

## 🖥️ Complete 15 Original Screens

| Screen # | Module / Feature | Web Implementation |
|---|---|---|
| **Screen 1** | User Login | `POST /api/auth/login` + Auth Modal |
| **Screen 2** | User Signup | `POST /api/auth/signup` + Registration Tab |
| **Screen 3** | Dashboard Overview | Glassmorphic KPI cards, Top Performers Leaderboard |
| **Screen 4** | Add Student | Modal with Form Validation (`POST /api/students`) |
| **Screen 5** | View Student List | Responsive Table with Live Search Filter |
| **Screen 6** | Update Student | Pre-filled Edit Modal (`PUT /api/students/<id>`) |
| **Screen 7** | Delete Student | Protected Delete Action (`DELETE /api/students/<id>`) |
| **Screen 8** | Add Attendance | Single & Fast Bulk Attendance Marking |
| **Screen 9** | View Attendance | Date & Student Filtered Register with Status Pills |
| **Screen 10** | Add Marks | Subject Exam Entry (`POST /api/marks`) |
| **Screen 11** | View Marks | Scores, Progress Bar, Percentage & Letter Grades |
| **Screen 12** | Bar Graph - Marks Analysis | Interactive Chart.js Bar Chart (replaces Matplotlib) |
| **Screen 13** | Pie Chart - Attendance | Interactive Donut/Pie Chart (Present vs Absent %) |
| **Screen 14** | Full Comprehensive Report | Consolidated Multi-Table Joined Register |
| **Screen 15** | Export Report | One-click **Export to TXT** (original spec) & **CSV** |

---

## 🛠️ Tech Stack & Architecture
- **Backend:** Python Flask 3.1, SQLite 3 (pre-seeded from `student_db.sql`) with optional MySQL dual-support.
- **Frontend:** Vanilla HTML5, Modern CSS Design System (Dark/Light mode, Glassmorphism, Responsive Grid), Chart.js 4.4, FontAwesome 6, Google Fonts (*Outfit* & *Inter*).
- **Database File:** `student_db.sqlite`
