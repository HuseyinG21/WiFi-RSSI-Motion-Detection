
import socket
import threading
import tkinter as tk
from tkinter import ttk
import time

from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PORT = 6000

boards = {
    "UNO1": {"signal":"--","avg":"--","rate":"--","last":0,"history":deque(maxlen=100)},
    "UNO2": {"signal":"--","avg":"--","rate":"--","last":0,"history":deque(maxlen=100)},
    "UNO3": {"signal":"--","avg":"--","rate":"--","last":0,"history":deque(maxlen=100)},
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

def receiver():
    while True:
        try:
            data,_ = sock.recvfrom(1024)
            b,s,a,r = data.decode().split(",")
            if b in boards:
                boards[b]["signal"]=s
                boards[b]["avg"]=a
                boards[b]["rate"]=r
                boards[b]["last"]=time.time()
                
                try:
                    boards[b]["history"].append(int(s))
                except:
                    pass
        except Exception:
            pass

threading.Thread(target=receiver,daemon=True).start()

root=tk.Tk()
root.title("WiFi Motion Detection System")
root.geometry("900x650")

title=tk.Label(root,text="WiFi Motion Detection System",
               font=("Arial",20,"bold"))
title.pack(pady=10)

frames={}
labels={}
bars={}

for name in ["UNO1","UNO2","UNO3"]:
    f=tk.LabelFrame(root,text=name,font=("Arial",12,"bold"))
    f.pack(fill="x",padx=15,pady=8)
    lbl=tk.Label(f,font=("Consolas",12),justify="left")
    lbl.pack(side="left",padx=10,pady=8)
    pb=ttk.Progressbar(f,length=300,maximum=40)
    pb.pack(side="right",padx=15)
    frames[name]=f
    labels[name]=lbl
    bars[name]=pb

status=tk.Label(root,text="🟢 CLEAR",fg="green",
                font=("Arial",22,"bold"))
status.pack(pady=15)
fig = Figure(figsize=(8,3), dpi=100)

ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)

canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

def update():
    online_count=0
    drop_count=0

    for name,d in boards.items():
        online=(time.time()-d["last"])<2

        if online:
            state="🟢 ONLINE"
            online_count+=1
        else:
            state="🔴 OFFLINE"

        sig=d["signal"]
        avg=d["avg"]
        rate=d["rate"]

        labels[name]["text"]=(
            f"{state}\n\n"
            f"Signal   : {sig} dBm\n"
            f"Average  : {avg} dBm\n"
            f"Rate     : {rate} Mbps"
        )

        try:
            val=max(0,min(40,int(sig)+80))
            bars[name]["value"]=val
            if int(sig)<=-55:
                drop_count+=1
        except:
            bars[name]["value"]=0

    if drop_count>=2:
        status.config(text="🚨 HUMAN DETECTED",fg="red")
    else:
        status.config(text="🟢 CLEAR",fg="green")
     
    
     
    ax.clear()

    colors = {
        "UNO1":"blue",
        "UNO2":"green",
        "UNO3":"orange"
    }

    for name,d in boards.items():

        if len(d["history"]) > 1:

            ax.plot(
                list(d["history"]),
                label=name,
                color=colors[name]
            )

    ax.set_title("Live RSSI")

    ax.set_ylabel("dBm")

    ax.set_ylim(-80,-30)

    ax.grid(True)

    ax.legend()

    canvas.draw_idle()

    root.after(100, update)

update()
root.mainloop()

