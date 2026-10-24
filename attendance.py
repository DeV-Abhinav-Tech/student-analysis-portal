import tkinter as tk
from tkinter import ttk
from db_config import get_connection
from datetime import date
def open_attendance(mode="view"):
    win=tk.Toplevel(); win.geometry("700x400"); win.title("Attendance")
    def load():
        for i in tree.get_children(): tree.delete(i)
        con=get_connection(); cur=con.cursor()
        cur.execute("SELECT a.id, s.name, a.att_date, a.status FROM attendance a JOIN students s ON a.student_id=s.id")
        for r in cur.fetchall(): tree.insert("", tk.END, values=r)
        con.close()
    def add():
        con=get_connection(); cur=con.cursor()
        cur.execute("INSERT INTO attendance(student_id, att_date, status) VALUES(%s,%s,%s)",(e1.get(), date.today(), e2.get()))
        con.commit(); con.close(); load()
    f=tk.Frame(win); f.pack()
    if mode=="add":
        tk.Label(f,text="Student ID").grid(row=0,column=0); e1=tk.Entry(f); e1.grid(row=0,column=1)
        tk.Label(f,text="Status P/A").grid(row=0,column=2); e2=tk.Entry(f); e2.grid(row=0,column=3)
        tk.Button(f,text="Mark Attendance", command=add).grid(row=0,column=4, padx=10)
    tree=ttk.Treeview(win, columns=("ID","Student","Date","Status"), show="headings")
    for c in ("ID","Student","Date","Status"): tree.heading(c,text=c)
    tree.pack(fill=tk.BOTH, expand=True); load()