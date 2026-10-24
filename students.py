import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection

def open_students(mode="view"):
    win=tk.Toplevel(); win.geometry("900x500"); win.title(f"Students - {mode}")
    def load():
        for i in tree.get_children(): tree.delete(i)
        con=get_connection(); cur=con.cursor(); cur.execute("SELECT * FROM students")
        for r in cur.fetchall(): tree.insert("", tk.END, values=r)
        con.close()
    def add():
        con=get_connection(); cur=con.cursor()
        cur.execute("INSERT INTO students(name,roll_no,class,city,phone) VALUES(%s,%s,%s,%s,%s)",(e1.get(),e2.get(),e3.get(),e4.get(),e5.get()))
        con.commit(); con.close(); load()
    def update():
        con=get_connection(); cur=con.cursor()
        cur.execute("UPDATE students SET name=%s, city=%s WHERE roll_no=%s",(e1.get(),e4.get(),e2.get()))
        con.commit(); con.close(); load()
    def delete():
        con=get_connection(); cur=con.cursor()
        cur.execute("DELETE FROM students WHERE roll_no=%s",(e2.get(),))
        con.commit(); con.close(); load()

    f=tk.Frame(win); f.pack(pady=10)
    tk.Label(f,text="Name").grid(row=0,column=0); e1=tk.Entry(f); e1.grid(row=0,column=1)
    tk.Label(f,text="Roll No").grid(row=0,column=2); e2=tk.Entry(f); e2.grid(row=0,column=3)
    tk.Label(f,text="Class").grid(row=1,column=0); e3=tk.Entry(f); e3.grid(row=1,column=1)
    tk.Label(f,text="City").grid(row=1,column=2); e4=tk.Entry(f); e4.grid(row=1,column=3)
    tk.Label(f,text="Phone").grid(row=1,column=4); e5=tk.Entry(f); e5.grid(row=1,column=5)

    if mode=="add": tk.Button(f,text="Add", bg="green", fg="white", command=add).grid(row=0,column=6, padx=10)
    if mode=="update": tk.Button(f,text="Update", bg="blue", fg="white", command=update).grid(row=0,column=6, padx=10)
    if mode=="delete": tk.Button(f,text="Delete", bg="red", fg="white", command=delete).grid(row=0,column=6, padx=10)

    tree=ttk.Treeview(win, columns=("ID","Name","Roll","Class","City","Phone"), show="headings")
    for c in ("ID","Name","Roll","Class","City","Phone"): tree.heading(c,text=c)
    tree.pack(fill=tk.BOTH, expand=True); load()