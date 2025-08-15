import customtkinter as ctk
import sqlite3
from tkinter import messagebox
import qrcode
from io import BytesIO
from PIL import Image, ImageTk

DB_PATH = r"D:\PYTHON\LMS 2.0\library.db"

# ---------- Database Helper ----------
def get_conn():
    return sqlite3.connect(DB_PATH)

def add_book_to_db(title, author, category, total_copies):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, category, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
            (title, author, category, total_copies, total_copies)
        )
        conn.commit()
        return cursor.lastrowid  # return the book_id

# ---------- AddBookPage ----------
class AddBookPage(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="#1E1E1E")

        # ---------- Title ----------
        ctk.CTkLabel(
            self,
            text="➕ Add New Book",
            font=("Arial", 22, "bold"),
            text_color="#E0E0E0"
        ).pack(anchor="w", padx=10, pady=(10,5))

        ctk.CTkLabel(
            self,
            text="Fill the details below to add a new book to the library",
            font=("Arial", 13),
            text_color="#AFAFAF"
        ).pack(anchor="w", padx=10, pady=(0,10))

        # ---------- Form ----------
        form_frame = ctk.CTkFrame(self, fg_color="#2E2E2E", corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(form_frame, text="Book Title:", text_color="#E0E0E0").pack(anchor="w", padx=12, pady=(12,0))
        self.title_entry = ctk.CTkEntry(form_frame)
        self.title_entry.pack(fill="x", padx=12, pady=5)

        # Author
        ctk.CTkLabel(form_frame, text="Author:", text_color="#E0E0E0").pack(anchor="w", padx=12, pady=(12,0))
        self.author_entry = ctk.CTkEntry(form_frame)
        self.author_entry.pack(fill="x", padx=12, pady=5)

        # Category
        ctk.CTkLabel(form_frame, text="Category:", text_color="#E0E0E0").pack(anchor="w", padx=12, pady=(12,0))
        self.category_entry = ctk.CTkEntry(form_frame)
        self.category_entry.pack(fill="x", padx=12, pady=5)

        # Total Copies
        ctk.CTkLabel(form_frame, text="Total Copies:", text_color="#E0E0E0").pack(anchor="w", padx=12, pady=(12,0))
        self.copies_entry = ctk.CTkEntry(form_frame)
        self.copies_entry.pack(fill="x", padx=12, pady=5)

        # Status Label
        self.status_label = ctk.CTkLabel(form_frame, text="", text_color="#AFAFAF")
        self.status_label.pack(pady=(10,0))

        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=10)
        ctk.CTkButton(btn_frame, text="Add Book", fg_color="green", command=self.add_book).pack(side="left")
        ctk.CTkButton(btn_frame, text="Reset Form", fg_color="#3A3A3A", command=self.reset_form).pack(side="left", padx=10)

        # QR Code Display
        self.qr_label = ctk.CTkLabel(form_frame, text="")
        self.qr_label.pack(pady=10)

    # ---------- Form Actions ----------
    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        category = self.category_entry.get().strip()
        copies = self.copies_entry.get().strip()

        if not title or not copies:
            self.status_label.configure(text="Title and Total Copies are required!", text_color="#FF6666")
            return

        try:
            copies_int = int(copies)
            if copies_int <= 0:
                raise ValueError
        except ValueError:
            self.status_label.configure(text="Total Copies must be a positive number.", text_color="#FF6666")
            return

        # Insert into DB
        try:
            book_id = add_book_to_db(title, author, category, copies_int)
            self.status_label.configure(text=f"✅ Book '{title}' added successfully!", text_color="#00FF88")
            self.generate_qr(book_id)
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="#FF6666")

    def reset_form(self):
        self.title_entry.delete(0, "end")
        self.author_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.copies_entry.delete(0, "end")
        self.status_label.configure(text="")
        self.qr_label.configure(image="", text="")

    # ---------- QR Code ----------
    def generate_qr(self, book_id):
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(str(book_id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((120,120))
        self.qr_img = ImageTk.PhotoImage(img)
        self.qr_label.configure(image=self.qr_img, text="")
