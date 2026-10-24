import tkinter as tk
from tkinter import ttk
from db_config import get_connection
def open_marks(mode="view"):
    win=tk.Toplevel(); win.geometry("700x400"); win.title("Marks")
    def load():
        for i in tree.get_children(): tree.delete(i)
        con=get_connection(); cur=con.cursor()
        cur.execute("SELECT m.id, s.name, m.subject, m.marks_obtained, m.total_marks FROM marks m JOIN students s ON m.student_id=s.id")
        for r in cur.fetchall(): tree.insert("", tk.END, values=r)
        con.close()
    def add():
        con=get_connection(); cur=con.cursor()
        cur.execute("INSERT INTO marks(student_id, subject, marks_obtained, total_marks) VALUES(%s,%s,%s,%s)",(e1.get(), e2.get(), e3.get(), e4.get()))
        con.commit(); con.close(); load()
    f=tk.Frame(win); f.pack()
    if mode=="add":
        tk.Label(f,text="Stud ID").grid(row=0,column=0); e1=tk.Entry(f); e1.grid(row=0,column=1)
        tk.Label(f,text="Subject").grid(row=0,column=2); e2=tk.Entry(f); e2.grid(row=0,column=3)
        tk.Label(f,text="Obt").grid(row=1,column=0); e3=tk.Entry(f); e3.grid(row=1,column=1)
        tk.Label(f,text="Total").grid(row=1,column=2); e4=tk.Entry(f); e4.grid(row=1,column=3)
        tk.Button(f,text="Add Marks", command=add).grid(row=1,column=4)
    tree=ttk.Treeview(win, columns=("ID","Student","Subject","Obt","Total"), show="headings")
    for c in ("ID","Student","Subject","Obt","Total"): tree.heading(c,text=c)
    tree.pack(fill=tk.BOTH, expand=True); load()