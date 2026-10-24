import tkinter as tk
from students import open_students
from attendance import open_attendance
from marks import open_marks
from analysis import open_analysis
from reports import open_reports

def open_dashboard():
    d=tk.Tk(); d.geometry("600x600"); d.title("Dashboard - 15 Screens")
    tk.Label(d,text="DASHBOARD - STUDENT ANALYSIS", font=("Arial",16,"bold")).pack(pady=15)
    tk.Button(d,text="4. Add Student", width=30, command=lambda: open_students("add")).pack(pady=5)
    tk.Button(d,text="5. View Student List", width=30, command=lambda: open_students("view")).pack(pady=5)
    tk.Button(d,text="6. Update Student", width=30, command=lambda: open_students("update")).pack(pady=5)
    tk.Button(d,text="7. Delete Student", width=30, command=lambda: open_students("delete")).pack(pady=5)
    tk.Button(d,text="8. Add Attendance", width=30, command=lambda: open_attendance("add")).pack(pady=5)
    tk.Button(d,text="9. View Attendance", width=30, command=lambda: open_attendance("view")).pack(pady=5)
    tk.Button(d,text="10. Add Marks", width=30, command=lambda: open_marks("add")).pack(pady=5)
    tk.Button(d,text="11. View Marks", width=30, command=lambda: open_marks("view")).pack(pady=5)
    tk.Button(d,text="12. Bar Graph - Marks Analysis", width=30, command=lambda: open_analysis("bar")).pack(pady=5)
    tk.Button(d,text="13. Pie Chart - Attendance", width=30, command=lambda: open_analysis("pie")).pack(pady=5)
    tk.Button(d,text="14. Full Report", width=30, command=open_reports).pack(pady=5)
    tk.Button(d,text="15. Export Report", width=30, bg="orange", command=open_reports).pack(pady=5)
    tk.Button(d,text="Exit", width=30, bg="red", fg="white", command=d.destroy).pack(pady=20)
    d.mainloop()