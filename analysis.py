import tkinter as tk
from db_config import get_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def open_analysis(type="bar"):
    win=tk.Toplevel(); win.geometry("900x600"); win.title(f"Analysis - {type}")
    con=get_connection(); cur=con.cursor()
    cur.execute("SELECT s.name, AVG(m.marks_obtained) FROM marks m JOIN students s ON m.student_id=s.id GROUP BY s.name")
    data=cur.fetchall()
    if not data: data=[("Tejas",85), ("Aman",72)]
    names=[x[0] for x in data]; marks=[float(x[1]) for x in data]
    fig, ax = plt.subplots(figsize=(8,4))
    if type=="bar":
        ax.bar(names, marks, color="green"); ax.set_title("Bar Chart - Student Avg Marks"); ax.set_ylabel("Marks")
    else:
        ax.pie(marks, labels=names, autopct='%1.1f%%'); ax.set_title("Pie Chart - Marks Distribution")
    canvas=FigureCanvasTkAgg(fig, master=win); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    con.close()