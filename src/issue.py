import sqlite3
from datetime import datetime, timedelta
import customtkinter as ctk

DB_PATH = "library.db"
MAX_ISSUES_PER_MEMBER = 3
DEFAULT_LOAN_DAYS = 14
DATE_FMT = "%Y-%m-%d"  # YYYY-MM-DD

# -----------------------------
# Database helpers
# -----------------------------

def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables if not exist. Call this once on app start."""
    with get_conn() as con:
        cur = con.cursor()
        # Minimal book + member + issue schema
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                category TEXT,
                total_copies INTEGER NOT NULL DEFAULT 1,
                available_copies INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL CHECK(status IN ('issued','returned','overdue')) DEFAULT 'issued',
                FOREIGN KEY(book_id) REFERENCES books(book_id),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            );
            """
        )
        con.commit()


def seed_sample_data():
    """Optional: add some rows if tables are empty so the page is testable."""
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM books")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO books (title, author, category, total_copies, available_copies) VALUES (?,?,?,?,?)",
                [
                    ("Quantum Physics 101", "A. Einstein", "Science", 3, 3),
                    ("Discrete Math", "R. Graham", "Math", 2, 2),
                    ("World History", "J. Roberts", "History", 1, 1),
                    ("Modern Web Dev", "S. Lee", "Technology", 4, 4),
                    ("Mystery Tales", "N. Knox", "Fiction", 5, 5),
                ],
            )
        cur.execute("SELECT COUNT(*) FROM members")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO members (name, email) VALUES (?,?)",
                [
                    ("Bhargav Narayan", "bhargav@example.com"),
                    ("Asha P.", "asha@example.com"),
                    ("Vikram S.", "vikram@example.com"),
                ],
            )
        con.commit()


# -----------------------------
# Query helpers
# -----------------------------

def find_book(identifier: str):
    """Lookup by numeric ID or partial title."""
    with get_conn() as con:
        cur = con.cursor()
        if identifier.isdigit():
            cur.execute("SELECT book_id, title, author, category, available_copies FROM books WHERE book_id=?", (int(identifier),))
            row = cur.fetchone()
            return [row] if row else []
        # partial title match
        cur.execute(
            "SELECT book_id, title, author, category, available_copies FROM books WHERE title LIKE ? ORDER BY title LIMIT 10",
            (f"%{identifier}%",),
        )
        return cur.fetchall()


def find_member(identifier: str):
    """Lookup by numeric ID or partial name."""
    with get_conn() as con:
        cur = con.cursor()
        if identifier.isdigit():
            cur.execute("SELECT member_id, name, email FROM members WHERE member_id=?", (int(identifier),))
            row = cur.fetchone()
            return [row] if row else []
        cur.execute(
            "SELECT member_id, name, email FROM members WHERE name LIKE ? ORDER BY name LIMIT 10",
            (f"%{identifier}%",),
        )
        return cur.fetchall()


def active_issues_for_member(member_id: int) -> int:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM issues WHERE member_id=? AND status='issued'",
            (member_id,),
        )
        return cur.fetchone()[0]


def is_book_available(book_id: int) -> bool:
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT available_copies FROM books WHERE book_id=?", (book_id,))
        row = cur.fetchone()
        return row is not None and row[0] > 0


def perform_issue(book_id: int, member_id: int, issue_date: str, due_date: str):
    """Create issue row + decrement availability inside a transaction."""
    with get_conn() as con:
        cur = con.cursor()
        # Check again inside transaction
        cur.execute("SELECT available_copies FROM books WHERE book_id=?", (book_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Book not found")
        if row[0] <= 0:
            raise ValueError("No available copies to issue")

        cur.execute(
            "INSERT INTO issues (book_id, member_id, issue_date, due_date, status) VALUES (?,?,?,?, 'issued')",
            (book_id, member_id, issue_date, due_date),
        )
        cur.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE book_id=?",
            (book_id,),
        )
        con.commit()


# -----------------------------
# UI: IssueBookPage
# -----------------------------

class IssueBookPage(ctk.CTkFrame):
    """A self-contained Issue Book form that fits into your dark dashboard.

    Usage:
        page = IssueBookPage(parent_frame)
        page.pack(fill="both", expand=True)
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="#1E1E1E")

        # Internal state
        self.selected_book = None   # (book_id, title, author, category, available)
        self.selected_member = None # (member_id, name, email)

        # ---------- Title Bar ----------
        header = ctk.CTkFrame(self, fg_color="#1E1E1E")
        header.pack(fill="x", padx=10, pady=(10, 0))

        title = ctk.CTkLabel(
            header,
            text="📖 Issue Book",
            font=("Arial", 22, "bold"),
            text_color="#E0E0E0",
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header,
            text="Fill the details below to issue a book to a member",
            font=("Arial", 13),
            text_color="#AFAFAF",
        )
        subtitle.pack(side="left", padx=12)

        # ---------- Content Grid ----------
        content = ctk.CTkFrame(self, fg_color="#1E1E1E")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Member Panel
        member_card = self._build_card(content, "👤 Member Details")
        member_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))

        self.member_query = ctk.CTkEntry(member_card, placeholder_text="Member ID or Name")
        self.member_query.pack(fill="x", padx=12, pady=(8, 6))

        member_btns = ctk.CTkFrame(member_card, fg_color="transparent")
        member_btns.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(member_btns, text="Lookup", command=self.lookup_member).pack(side="left")
        ctk.CTkButton(member_btns, text="Clear", command=self.clear_member, fg_color="#3A3A3A").pack(side="left", padx=8)

        self.member_info = ctk.CTkLabel(member_card, text="No member selected", text_color="#AFAFAF")
        self.member_info.pack(fill="x", padx=12, pady=(6, 12))

        # Right: Book Panel
        book_card = self._build_card(content, "📚 Book Details")
        book_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))

        self.book_query = ctk.CTkEntry(book_card, placeholder_text="Book ID or Title")
        self.book_query.pack(fill="x", padx=12, pady=(8, 6))

        book_btns = ctk.CTkFrame(book_card, fg_color="transparent")
        book_btns.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(book_btns, text="Lookup", command=self.lookup_book).pack(side="left")
        ctk.CTkButton(book_btns, text="Clear", command=self.clear_book, fg_color="#3A3A3A").pack(side="left", padx=8)

        self.book_info = ctk.CTkLabel(book_card, text="No book selected", text_color="#AFAFAF")
        self.book_info.pack(fill="x", padx=12, pady=(6, 12))

        # Issue Settings
        issue_card = self._build_card(content, "🗓 Issue Settings")
        issue_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(8, 8))

        row1 = ctk.CTkFrame(issue_card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(8, 4))

        # Issue date
        ctk.CTkLabel(row1, text="Issue Date (YYYY-MM-DD)", text_color="#E0E0E0").pack(side="left")
        self.issue_date_entry = ctk.CTkEntry(row1, width=160)
        self.issue_date_entry.pack(side="left", padx=(10, 20))
        self.issue_date_entry.insert(0, datetime.today().strftime(DATE_FMT))

        # Loan period chooser
        ctk.CTkLabel(row1, text="Loan Days", text_color="#E0E0E0").pack(side="left")
        self.loan_days = ctk.CTkOptionMenu(row1, values=["7", "14", "21", "28"], command=self._refresh_due_date)
        self.loan_days.pack(side="left", padx=(10, 20))
        self.loan_days.set(str(DEFAULT_LOAN_DAYS))

        # Due date (read-only)
        ctk.CTkLabel(row1, text="Due Date", text_color="#E0E0E0").pack(side="left")
        self.due_date_entry = ctk.CTkEntry(row1, width=160)
        self.due_date_entry.pack(side="left", padx=(10, 0))
        self._refresh_due_date()
        self._set_entry_readonly(self.due_date_entry)

        # Action buttons
        actions = ctk.CTkFrame(issue_card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(8, 12))
        ctk.CTkButton(actions, text="Issue Book", height=38, command=self.issue_book).pack(side="left")
        ctk.CTkButton(actions, text="Reset Form", height=38, fg_color="#3A3A3A", command=self.reset_form).pack(side="left", padx=8)

        # Status
        self.status = ctk.CTkLabel(self, text="", text_color="#AFAFAF")
        self.status.pack(fill="x", padx=12, pady=(4, 10))

        # Configure grid weights
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)

    # ---------- UI helpers ----------
    def _build_card(self, master, title: str):
        card = ctk.CTkFrame(master, corner_radius=15, fg_color="#2E2E2E", border_width=2, border_color="#3A3A3A")
        header = ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), text_color="#E0E0E0")
        header.pack(anchor="w", padx=12, pady=(10, 6))
        return card

    def _set_entry_readonly(self, entry: ctk.CTkEntry):
        entry.configure(state="normal")
        entry.configure(state="readonly")

    def _refresh_due_date(self, *_):
        try:
            base = datetime.strptime(self.issue_date_entry.get().strip(), DATE_FMT)
        except Exception:
            base = datetime.today()
        days = int(self.loan_days.get())
        due = base + timedelta(days=days)
        self.due_date_entry.configure(state="normal")
        self.due_date_entry.delete(0, "end")
        self.due_date_entry.insert(0, due.strftime(DATE_FMT))
        self._set_entry_readonly(self.due_date_entry)

    def _set_status(self, msg: str, ok: bool = True):
        self.status.configure(text=msg, text_color="#00FF88" if ok else "#FF6666")

    # ---------- Lookups ----------
    def lookup_member(self):
        query = self.member_query.get().strip()
        if not query:
            self._set_status("Enter a Member ID or Name to search.", ok=False)
            return
        results = find_member(query)
        if not results:
            self.selected_member = None
            self.member_info.configure(text="No member found.")
            self._set_status("No matching member.", ok=False)
            return
        # Pick first result for simplicity; you can extend to show a list popup
        m = results[0]
        self.selected_member = m  # (member_id, name, email)
        active = active_issues_for_member(m[0])
        self.member_info.configure(
            text=f"ID: {m[0]}\nName: {m[1]}\nEmail: {m[2] or '-'}\nActive Issues: {active}/{MAX_ISSUES_PER_MEMBER}",
            text_color="#E0E0E0",
        )
        self._set_status("Member selected.")

    def clear_member(self):
        self.member_query.delete(0, "end")
        self.member_info.configure(text="No member selected", text_color="#AFAFAF")
        self.selected_member = None

    def lookup_book(self):
        query = self.book_query.get().strip()
        if not query:
            self._set_status("Enter a Book ID or Title to search.", ok=False)
            return
        results = find_book(query)
        if not results:
            self.selected_book = None
            self.book_info.configure(text="No book found.")
            self._set_status("No matching book.", ok=False)
            return
        b = results[0]
        self.selected_book = b  # (book_id, title, author, category, available)
        availability = "Available" if b[4] > 0 else "Not Available"
        # avail_color variable kept (not used) to avoid changing functionality
        avail_color = "#00FF88" if b[4] > 0 else "#FF6666"
        self.book_info.configure(
            text=f"ID: {b[0]}\nTitle: {b[1]}\nAuthor: {b[2] or '-'}\nCategory: {b[3] or '-'}\nAvailable Copies: {b[4]} ({availability})",
            text_color="#E0E0E0",
        )
        self._set_status(f"Book selected. {availability}")

    def clear_book(self):
        self.book_query.delete(0, "end")
        self.book_info.configure(text="No book selected", text_color="#AFAFAF")
        self.selected_book = None

    def reset_form(self):
        self.clear_book()
        self.clear_member()
        self.issue_date_entry.delete(0, "end")
        self.issue_date_entry.insert(0, datetime.today().strftime(DATE_FMT))
        self.loan_days.set(str(DEFAULT_LOAN_DAYS))
        self._refresh_due_date()
        self._set_status("")

    # ---------- Issue Action ----------
    def issue_book(self):
        # Validate selections
        if not self.selected_member:
            self._set_status("Select a member first.", ok=False)
            return
        if not self.selected_book:
            self._set_status("Select a book first.", ok=False)
            return
        mid = int(self.selected_member[0])
        bid = int(self.selected_book[0])

        # Policy checks
        active = active_issues_for_member(mid)
        if active >= MAX_ISSUES_PER_MEMBER:
            self._set_status(f"Member already has {active} active issues (limit {MAX_ISSUES_PER_MEMBER}).", ok=False)
            return
        if not is_book_available(bid):
            self._set_status("This book is not currently available.", ok=False)
            return

        # Dates
        try:
            issue_date = datetime.strptime(self.issue_date_entry.get().strip(), DATE_FMT)
        except Exception:
            self._set_status("Issue Date must be YYYY-MM-DD.", ok=False)
            return
        due_date = issue_date + timedelta(days=int(self.loan_days.get()))

        try:
            perform_issue(
                book_id=bid,
                member_id=mid,
                issue_date=issue_date.strftime(DATE_FMT),
                due_date=due_date.strftime(DATE_FMT),
            )
        except Exception as e:
            self._set_status(f"Failed to issue: {e}", ok=False)
            return

        # Update UI to reflect new availability
        self.lookup_book()
        self.lookup_member()
        self._set_status("✅ Book issued successfully!")


# -----------------------------
# Integration helpers for your main file
# -----------------------------

def clear_container(container):
    for w in container.winfo_children():
        w.destroy()

issue_window = None  # global variable to hold the window

def show_issue_book_page():
    global issue_window
    if issue_window is not None and issue_window.winfo_exists():
        # If window already exists, bring it to front
        issue_window.lift()
        return

    # Create a new window
    issue_window = ctk.CTkToplevel()
    issue_window.title("Issue Book")
    issue_window.geometry("800x500")

    # Add a back button at the top
    back_btn = ctk.CTkButton(issue_window, text="← Back", command=issue_window.destroy)
    back_btn.pack(anchor="nw", padx=10, pady=10)

    # Add the IssueBookPage frame inside this new window
    page = IssueBookPage(issue_window)
    page.pack(fill="both", expand=True, padx=10, pady=10)

    # Ensure window stays alive
    issue_window.protocol("WM_DELETE_WINDOW", lambda: close_issue_window())

def close_issue_window():
    global issue_window
    if issue_window is not None:
        issue_window.destroy()
        issue_window = None


# -----------------------------
# Standalone launcher
# -----------------------------
if __name__ == "__main__":
    # Theme (optional)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Ensure DB exists and has a bit of data for testing
    init_db()
    seed_sample_data()

    # Hidden root for the toplevel window
    root = ctk.CTk()
    root.withdraw()

    # Open the Issue Book window and enter the loop
    show_issue_book_page()
    root.mainloop()

