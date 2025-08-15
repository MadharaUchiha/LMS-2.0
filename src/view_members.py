import customtkinter as ctk
import sqlite3
import random

# ==========================
# Database constants & setup
# ==========================
DB_PATH = "library.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                semester TEXT,
                course TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('issued','returned','overdue')) DEFAULT 'issued'
            );
        """)
        con.commit()

def generate_unique_member_id():
    with get_conn() as con:
        cur = con.cursor()
        while True:
            new_id = random.randint(1000, 9999)
            cur.execute("SELECT 1 FROM members WHERE member_id=?", (new_id,))
            if not cur.fetchone():
                return new_id

def add_member_to_db(member_id, name, email, semester, course):
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO members (member_id, name, email, semester, course) VALUES (?,?,?,?,?)",
            (member_id, name, email, semester, course)
        )
        con.commit()

def seed_sample_data():
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM members")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO members (member_id, name, email, semester, course) VALUES (?,?,?,?,?)",
                [
                    (1000, "Bhargav Narayan", "bhargav@example.com", "Sem 1", "BCA"),
                    (1001, "Asha P.", "asha@example.com", "Sem 2", "BCOM"),
                    (1002, "Vikram S.", "vikram@example.com", "Sem 3", "BA")
                ]
            )
        con.commit()

def get_members(query: str = "") -> list:
    with get_conn() as con:
        cur = con.cursor()
        if query:
            if query.isdigit():
                cur.execute("SELECT member_id, name, email, semester, course FROM members WHERE member_id = ?", (int(query),))
            else:
                cur.execute("SELECT member_id, name, email, semester, course FROM members WHERE name LIKE ? ORDER BY name", (f"%{query}%",))
        else:
            cur.execute("SELECT member_id, name, email, semester, course FROM members ORDER BY name")
        return cur.fetchall()

def active_issues_for_member(member_id: int) -> int:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM issues WHERE member_id=? AND status='issued'", (member_id,))
        return cur.fetchone()[0]

# ==========================
# UI Class
# ==========================
class ViewMembersPage(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="#1E1E1E")

        # Add Member Card
        add_card = self._build_card(self, "➕ Add New Member")
        add_card.pack(fill="x", padx=10, pady=(10, 5))

        self.name_entry = ctk.CTkEntry(add_card, placeholder_text="Member Name")
        self.name_entry.pack(fill="x", padx=12, pady=4)

        self.email_entry = ctk.CTkEntry(add_card, placeholder_text="Email (optional)")
        self.email_entry.pack(fill="x", padx=12, pady=4)

        # Semester Dropdown
        self.sem_var = ctk.StringVar(value="Sem 1")
        self.sem_dropdown = ctk.CTkOptionMenu(
            add_card,
            values=[f"Sem {i}" for i in range(1, 7)],
            variable=self.sem_var
        )
        self.sem_dropdown.pack(fill="x", padx=12, pady=4)

        # Course Dropdown
        self.course_var = ctk.StringVar(value="BCA")
        self.course_dropdown = ctk.CTkOptionMenu(
            add_card,
            values=["BCA", "BCOM", "BA"],
            variable=self.course_var
        )
        self.course_dropdown.pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(add_card, text="Add Member", command=self.add_member).pack(padx=12, pady=8)

        # Search Card
        search_card = self._build_card(self, "🔍 Search Members")
        search_card.pack(fill="x", padx=10, pady=(10, 5))
        self.search_query = ctk.CTkEntry(search_card, placeholder_text="Member ID or Name")
        self.search_query.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(search_card, text="Search", command=self.search_members).pack(side="left", padx=12, pady=8)
        ctk.CTkButton(search_card, text="Show All", command=self.show_all_members, fg_color="#3A3A3A").pack(side="left", pady=8)

        # Results Card
        results_card = self._build_card(self, "📋 Member List")
        results_card.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.results_frame = ctk.CTkScrollableFrame(results_card, fg_color="#2E2E2E")
        self.results_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.status = ctk.CTkLabel(self, text="", text_color="#AFAFAF")
        self.status.pack(fill="x", padx=12, pady=(0, 10))

        self.show_all_members()

    def _build_card(self, master, title: str):
        card = ctk.CTkFrame(master, corner_radius=15, fg_color="#2E2E2E", border_width=2, border_color="#3A3A3A")
        ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), text_color="#E0E0E0").pack(anchor="w", padx=12, pady=(10, 6))
        return card

    def _set_status(self, msg: str, ok: bool = True):
        self.status.configure(text=msg, text_color="#00FF88" if ok else "#FF6666")

    def add_member(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        semester = self.sem_var.get()
        course = self.course_var.get()

        if not name:
            self._set_status("Name is required!", ok=False)
            return

        new_id = generate_unique_member_id()
        add_member_to_db(new_id, name, email, semester, course)
        self._set_status(f"Member '{name}' added with ID {new_id}", ok=True)
        self.show_all_members()

        # Clear inputs
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.sem_var.set("Sem 1")
        self.course_var.set("BCA")

    def search_members(self):
        query = self.search_query.get().strip()
        if not query:
            self._set_status("Enter a Member ID or Name to search.", ok=False)
            return
        members = get_members(query)
        self._display_members(members)

    def show_all_members(self):
        self.search_query.delete(0, "end")
        members = get_members()
        self._display_members(members)

    def _display_members(self, members: list):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        if not members:
            ctk.CTkLabel(self.results_frame, text="No members found.", text_color="#FF6666", font=("Arial", 14)).pack(pady=20)
            self._set_status("No matching members.", ok=False)
            return

        headers = ["ID", "Name", "Email", "Semester", "Course", "Active Issues"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.results_frame, text=header, font=("Arial", 14, "bold"), text_color="#E0E0E0").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        for row_idx, member in enumerate(members, start=1):
            member_id, name, email, semester, course = member
            active = active_issues_for_member(member_id)
            row_values = [member_id, name, email or "-", semester or "-", course or "-", active]
            for col, value in enumerate(row_values):
                ctk.CTkLabel(self.results_frame, text=str(value), text_color="#E0E0E0" if col != 2 else "#AFAFAF").grid(row=row_idx, column=col, padx=10, pady=5, sticky="w")

        self._set_status(f"Found {len(members)} members.", ok=True)

# ==========================
# Integration Helper
# ==========================
def show_view_members_page(parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()
    page = ViewMembersPage(parent_frame)
    page.pack(fill="both", expand=True, padx=10, pady=10)

init_db()
seed_sample_data()
