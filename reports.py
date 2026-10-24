import tkinter as tk
from tkinter import ttk
from db_config import get_connection
from datetime import datetime

def open_reports():
    win=tk.Toplevel(); win.geometry("900x500"); win.title("Reports - Screen 14 & 15")
    tree=ttk.Treeview(win, columns=("Roll","Name","Class","Subject","Marks","Attendance"), show="headings")
    for c in ("Roll","Name","Class","Subject","Marks","Attendance"): tree.heading(c,text=c)
    tree.pack(fill=tk.BOTH, expand=True)
    def load():
        for i in tree.get_children(): tree.delete(i)
        con=get_connection(); cur=con.cursor()
        cur.execute("SELECT s.roll_no, s.name, s.class, m.subject, m.marks_obtained, a.status FROM students s LEFT JOIN marks m ON s.id=m.student_id LEFT JOIN attendance a ON s.id=a.student_id")
        for r in cur.fetchall(): tree.insert("", tk.END, values=r)
        con.close()
    def export():
        with open(f"Student_Report_{datetime.now().strftime('%Y%m%d')}.txt","w") as f:
            f.write("STUDENT ANALYSIS REPORT\n")
            for item in tree.get_children():
                f.write(str(tree.item(item)['values'])+"\n")
    tk.Button(win,text="Refresh Report", command=load).pack(side=tk.LEFT, padx=20, pady=10)
    tk.Button(win,text="Export to TXT - Screen 15", bg="orange", command=export).pack(side=tk.LEFT, pady=10)
    load()