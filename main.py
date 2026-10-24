import tkinter as tk
from tkinter import messagebox
from db_config import get_connection
from dashboard import open_dashboard

def signup():
    con=get_connection(); cur=con.cursor()
    try:
        cur.execute("INSERT INTO users(username,password,email) VALUES(%s,%s,%s)",(u.get(), p.get(), e.get()))
        con.commit(); messagebox.showinfo("Done","Signup Success")
    except Exception as ex: messagebox.showerror("Error", str(ex))
    con.close()

def login():
    con=get_connection(); cur=con.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",(u.get(), p.get()))
    if cur.fetchone(): root.destroy(); open_dashboard()
    else: messagebox.showerror("Error","Invalid Login")
    con.close()

root=tk.Tk(); root.geometry("450x500"); root.title("Student Analysis - Login")
tk.Label(root,text="STUDENT ANALYSIS", font=("Arial",18,"bold")).pack(pady=20)
tk.Label(root,text="Username").pack(); u=tk.Entry(root,width=30); u.pack()
tk.Label(root,text="Password").pack(); p=tk.Entry(root,width=30,show="*"); p.pack()
tk.Label(root,text="Email for Signup").pack(); e=tk.Entry(root,width=30); e.pack()
tk.Button(root,text="LOGIN", bg="green", fg="white", width=25, command=login).pack(pady=10)
tk.Button(root,text="SIGNUP", bg="blue", fg="white", width=25, command=signup).pack()
root.mainloop()