import tkinter as tk
from tkinter import ttk, messagebox

# Function to handle login
def login():
    user = username_entry.get()
    pwd = password_entry.get()

    if user == "admin" and pwd == "1234":
        messagebox.showinfo("Login Successful", "Welcome to the Library Management System!")
        root.destroy()  # Later open dashboard
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to exit
def close_app():
    root.destroy()

# Main window
root = tk.Tk()
root.title("Library Management System - Login")
root.geometry("500x500")
root.configure(bg="#f5f5f5")  # Light background
root.resizable(False, False)

# Center frame
frame = tk.Frame(root, bg="white", bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=350)

# Title
title_label = tk.Label(frame, text="Library Management System", font=("Helvetica", 14, "bold"), bg="white", fg="#333")
title_label.pack(pady=(10, 5))

subtitle_label = tk.Label(frame, text="Please login to continue", font=("Helvetica", 10), bg="white", fg="#666")
subtitle_label.pack(pady=(0, 10))

# Username
username_label = tk.Label(frame, text="Username", font=("Helvetica", 10), bg="white", anchor="w")
username_label.pack(fill="x", padx=20)
username_entry = ttk.Entry(frame, font=("Helvetica", 11))
username_entry.pack(fill="x", padx=20, pady=(0, 10))

# Password
password_label = tk.Label(frame, text="Password", font=("Helvetica", 10), bg="white", anchor="w")
password_label.pack(fill="x", padx=20)
password_entry = ttk.Entry(frame, font=("Helvetica", 11), show="*")
password_entry.pack(fill="x", padx=20, pady=(0, 15))

# Buttons
btn_frame = tk.Frame(frame, bg="white")
btn_frame.pack(pady=(0, 5))

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)
style.map("TButton",
          foreground=[("active", "white")],
          background=[("active", "#007acc")])

login_btn = ttk.Button(btn_frame, text="Login", command=login)
login_btn.grid(row=0, column=0, padx=8 , pady=5)

exit_btn = ttk.Button(btn_frame, text="Exit", command=close_app)
exit_btn.grid(row=0, column=1, padx=8, pady=5)

root.mainloop()
