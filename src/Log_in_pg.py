import customtkinter as ctk
import time
import threading
import sqlite3
from tkinter import Menu, messagebox
from Home import show_home_page  # Import your actual Home page

DB_PATH = r"D:\PYTHON\LMS 2.0\library.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ======== Database Setup ========
def init_admin_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create admins table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    # Check if default admin exists
    cursor.execute("SELECT * FROM admins WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
    conn.close()

init_admin_db()  # Initialize DB at startup

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1000x600")
        self.resizable(False, False)

        # ===== Main container =====
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_container()

        outer_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        outer_frame.pack(expand=True, fill="both")

        # ===== Top-right settings icon =====
        settings_btn = ctk.CTkButton(
            outer_frame,
            text="⚙️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#444",
            command=self.show_settings_menu
        )
        settings_btn.place(relx=0.98, rely=0.02, anchor="ne")

        login_frame = ctk.CTkFrame(
            outer_frame,
            corner_radius=15,
            fg_color="#2b2b2b",
            width=350,
            height=300
        )
        login_frame.pack(expand=True)
        login_frame.pack_propagate(False)

        ctk.CTkLabel(
            login_frame,
            text="Login",
            font=("Arial", 24, "bold")
        ).pack(pady=(20, 10))

        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Username",
            width=250
        )
        self.username_entry.pack(pady=10)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Password",
            show="*",
            width=250
        )
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", lambda e: self.handle_login())

        login_btn = ctk.CTkButton(
            login_frame,
            text="Login",
            width=200,
            command=self.handle_login
        )
        login_btn.pack(pady=20)

        self.login_status = ctk.CTkLabel(
            login_frame,
            text="",
            text_color="red"
        )
        self.login_status.pack()

    # ===== Settings Menu =====
    def show_settings_menu(self):
        menu = Menu(self, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#444", activeforeground="white")
        menu.add_command(label="Get Help", command=lambda: print("Help clicked"))
        menu.add_command(label="Forget Password", command=lambda: print("Forget Password clicked"))
        menu.add_command(label="Add New Admin & Password", command=self.add_new_admin)
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    # ===== Add New Admin Flow =====
    def add_new_admin(self):
        verify_window = ctk.CTkToplevel()
        verify_window.title("Verify Old Admin")
        verify_window.geometry("300x200")

        ctk.CTkLabel(verify_window, text="Old Admin Username").pack(pady=5)
        old_username_entry = ctk.CTkEntry(verify_window)
        old_username_entry.pack(pady=5)

        ctk.CTkLabel(verify_window, text="Old Admin Password").pack(pady=5)
        old_password_entry = ctk.CTkEntry(verify_window, show="*")
        old_password_entry.pack(pady=5)

        def verify_old_admin():
            old_username = old_username_entry.get()
            old_password = old_password_entry.get()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (old_username, old_password))
            result = cursor.fetchone()
            conn.close()

            if result:
                verify_window.destroy()
                new_admin_window = ctk.CTkToplevel()
                new_admin_window.title("Add New Admin")
                new_admin_window.geometry("300x200")

                ctk.CTkLabel(new_admin_window, text="New Admin Username").pack(pady=5)
                new_username_entry = ctk.CTkEntry(new_admin_window)
                new_username_entry.pack(pady=5)

                ctk.CTkLabel(new_admin_window, text="New Admin Password").pack(pady=5)
                new_password_entry = ctk.CTkEntry(new_admin_window, show="*")
                new_password_entry.pack(pady=5)

                def save_new_admin():
                    new_username = new_username_entry.get()
                    new_password = new_password_entry.get()

                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "INSERT INTO admins (username, password) VALUES (?, ?)",
                            (new_username, new_password)
                        )
                        conn.commit()
                        messagebox.showinfo("Success", "New admin added successfully!")
                        new_admin_window.destroy()
                    except sqlite3.IntegrityError:
                        messagebox.showerror("Error", "Admin username already exists!")
                    conn.close()

                ctk.CTkButton(new_admin_window, text="Save", command=save_new_admin).pack(pady=10)

            else:
                messagebox.showerror("Error", "Old admin credentials are incorrect!")

        ctk.CTkButton(verify_window, text="Verify", command=verify_old_admin).pack(pady=10)

    # ===== Login =====
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == "admin" and password == "admin":
            self.show_loading()
        else:
            self.login_status.configure(text="Invalid username or password")

    # ===== Loading =====
    def show_loading(self):
        self.clear_container()
        loading_frame = ctk.CTkFrame(self.container)
        loading_frame.pack(expand=True)

        ctk.CTkLabel(loading_frame, text="Loading...", font=("Arial", 18)).pack(pady=20)
        progress = ctk.CTkProgressBar(loading_frame, mode="indeterminate")
        progress.pack(pady=20, padx=50)
        progress.start()

        def delayed_home():
            time.sleep(2)
            self.clear_container()
            show_home_page(self, self.container)

        threading.Thread(target=delayed_home, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
