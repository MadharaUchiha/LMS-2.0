import customtkinter as ctk
from tkinter import messagebox

# Theme settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # You can change to "green", "dark-blue", etc.

# Main App Window
app = ctk.CTk()
app.title("LMS - Login")
app.geometry("500x400")
app.resizable(False, False)

# Title
title_label = ctk.CTkLabel(
    app,
    text="📚 Library Management System",
    font=("Helvetica", 24, "bold"),
    text_color="#00FFFF"
)
title_label.pack(pady=30)

# Frame for form
login_frame = ctk.CTkFrame(app, corner_radius=15)
login_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Username Entry
username_entry = ctk.CTkEntry(
    login_frame,
    placeholder_text="Username",
    width=300,
    height=40,
    corner_radius=10
)
username_entry.pack(pady=15)

# Password Entry
password_entry = ctk.CTkEntry(
    login_frame,
    placeholder_text="Password",
    width=300,
    height=40,
    corner_radius=10,
    show="*"
)
password_entry.pack(pady=15)

# Login Button Action
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "admin":
        messagebox.showinfo("Login Successful", "Welcome to the Library!")
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

# Login Button
login_button = ctk.CTkButton(
    login_frame,
    text="Login",
    command=login,
    corner_radius=8,
    width=300,
    height=40,
    fg_color="#00BFFF",
    hover_color="#1E90FF"
)
login_button.pack(pady=20)

# Forgot Password Link
forgot_pass = ctk.CTkLabel(
    login_frame,
    text="Forgot Password?",
    text_color="#FF69B4",
    cursor="hand2"
)
forgot_pass.pack()

app.mainloop()
