import sqlite3
from datetime import datetime
import customtkinter as ctk

DB_PATH = "library.db"
DATE_FMT = "%Y-%m-%d"

# -----------------------------
# Database helpers
# -----------------------------

def get_conn():
    return sqlite3.connect(DB_PATH)

def find_book(identifier: str):
    with get_conn() as con:
        cur = con.cursor()
        if identifier.isdigit():
            cur.execute(
                "SELECT book_id, title, author, category, available_copies FROM books WHERE book_id=?",
                (int(identifier),),
            )
            row = cur.fetchone()
            return [row] if row else []
        cur.execute(
            "SELECT book_id, title, author, category, available_copies FROM books WHERE title LIKE ? ORDER BY title LIMIT 10",
            (f"%{identifier}%",),
        )
        return cur.fetchall()

def find_member(identifier: str):
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

def perform_return(issue_id: int, return_date: str):
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("UPDATE issues SET return_date=?, status='returned' WHERE issue_id=?", (return_date, issue_id))
        cur.execute(
            "UPDATE books SET available_copies = available_copies + 1 WHERE book_id=(SELECT book_id FROM issues WHERE issue_id=?)",
            (issue_id,),
        )
        con.commit()

# -----------------------------
# ReturnBookPage
# -----------------------------

class ReturnBookPage(ctk.CTkFrame):
    """Return Book page for main container (same window as IssueBookPage)"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="#1E1E1E")

        self.selected_member = None
        self.selected_book = None

        # ---------- Title ----------
        header = ctk.CTkFrame(self, fg_color="#1E1E1E")
        header.pack(fill="x", padx=10, pady=(10,0))

        title = ctk.CTkLabel(header, text="📗 Return Book", font=("Arial",22,"bold"), text_color="#E0E0E0")
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Select member & book to return", font=("Arial",13), text_color="#AFAFAF")
        subtitle.pack(side="left", padx=12)

        # ---------- Content ----------
        content = ctk.CTkFrame(self, fg_color="#1E1E1E")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Member Card
        member_card = self._build_card(content, "👤 Member Details")
        member_card.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=(0,8))

        self.member_query = ctk.CTkEntry(member_card, placeholder_text="Member ID or Name")
        self.member_query.pack(fill="x", padx=12, pady=(8,6))

        member_btns = ctk.CTkFrame(member_card, fg_color="transparent")
        member_btns.pack(fill="x", padx=12, pady=(0,8))
        ctk.CTkButton(member_btns, text="Lookup", command=self.lookup_member).pack(side="left")
        ctk.CTkButton(member_btns, text="Clear", command=self.clear_member, fg_color="#3A3A3A").pack(side="left", padx=8)

        self.member_info = ctk.CTkLabel(member_card, text="No member selected", text_color="#AFAFAF")
        self.member_info.pack(fill="x", padx=12, pady=(6,12))

        # Right: Book Card
        book_card = self._build_card(content, "📚 Book Details")
        book_card.grid(row=0, column=1, sticky="nsew", padx=(8,0), pady=(0,8))

        self.book_query = ctk.CTkEntry(book_card, placeholder_text="Book ID or Title")
        self.book_query.pack(fill="x", padx=12, pady=(8,6))

        book_btns = ctk.CTkFrame(book_card, fg_color="transparent")
        book_btns.pack(fill="x", padx=12, pady=(0,8))
        ctk.CTkButton(book_btns, text="Lookup", command=self.lookup_book).pack(side="left")
        ctk.CTkButton(book_btns, text="Clear", command=self.clear_book, fg_color="#3A3A3A").pack(side="left", padx=8)
        ctk.CTkButton(book_btns, text="Scan QR", command=lambda: None).pack(side="left", padx=8)

        self.book_info = ctk.CTkLabel(book_card, text="No book selected", text_color="#AFAFAF")
        self.book_info.pack(fill="x", padx=12, pady=(6,12))

        # Action Card
        action_card = self._build_card(content, "🔄 Return Settings")
        action_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(8,8))

        row1 = ctk.CTkFrame(action_card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(8,4))

        ctk.CTkLabel(row1, text="Return Date (YYYY-MM-DD)", text_color="#E0E0E0").pack(side="left")
        self.return_date_entry = ctk.CTkEntry(row1, width=160)
        self.return_date_entry.pack(side="left", padx=(10,20))
        self.return_date_entry.insert(0, datetime.today().strftime(DATE_FMT))

        # Buttons
        actions = ctk.CTkFrame(action_card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(8,12))
        ctk.CTkButton(actions, text="Return Book", height=38, command=self.return_book).pack(side="left")
        ctk.CTkButton(actions, text="Reset Form", height=38, fg_color="#3A3A3A", command=self.reset_form).pack(side="left", padx=8)

        # Status
        self.status = ctk.CTkLabel(self, text="", text_color="#AFAFAF")
        self.status.pack(fill="x", padx=12, pady=(4,10))

        # Grid config
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)

    # ---------- UI helpers ----------
    def _build_card(self, master, title: str):
        card = ctk.CTkFrame(master, corner_radius=15, fg_color="#2E2E2E", border_width=2, border_color="#3A3A3A")
        header = ctk.CTkLabel(card, text=title, font=("Arial",16,"bold"), text_color="#E0E0E0")
        header.pack(anchor="w", padx=12, pady=(10,6))
        return card

    def _set_status(self, msg: str, ok: bool=True):
        self.status.configure(text=msg, text_color="#00FF88" if ok else "#FF6666")

    # ---------- Lookup ----------
    def lookup_member(self):
        query = self.member_query.get().strip()
        if not query:
            self._set_status("Enter a Member ID or Name.", ok=False)
            return
        results = find_member(query)
        if not results:
            self.selected_member = None
            self.member_info.configure(text="No member found.")
            self._set_status("No matching member.", ok=False)
            return
        m = results[0]
        self.selected_member = m
        self.member_info.configure(
            text=f"ID: {m[0]}\nName: {m[1]}\nEmail: {m[2] or '-'}",
            text_color="#E0E0E0"
        )
        self._set_status("Member selected.")

    def clear_member(self):
        self.member_query.delete(0,"end")
        self.member_info.configure(text="No member selected", text_color="#AFAFAF")
        self.selected_member = None

    def lookup_book(self):
        query = self.book_query.get().strip()
        if not query:
            self._set_status("Enter Book ID or Title.", ok=False)
            return
        results = find_book(query)
        if not results:
            self.selected_book = None
            self.book_info.configure(text="No book found", text_color="#AFAFAF")
            self._set_status("No matching book.", ok=False)
            return
        b = results[0]
        self.selected_book = b
        self.book_info.configure(
            text=f"ID: {b[0]}\nTitle: {b[1]}\nAuthor: {b[2] or '-'}\nCategory: {b[3] or '-'}\nAvailable Copies: {b[4]}",
            text_color="#E0E0E0"
        )
        self._set_status("Book selected.")

    def clear_book(self):
        self.book_query.delete(0,"end")
        self.book_info.configure(text="No book selected", text_color="#AFAFAF")
        self.selected_book = None

    def reset_form(self):
        self.clear_member()
        self.clear_book()
        self.return_date_entry.delete(0,"end")
        self.return_date_entry.insert(0, datetime.today().strftime(DATE_FMT))
        self._set_status("")

    # ---------- Return action ----------
    def return_book(self):
        try:
            if not self.selected_member:
                self._set_status("Select a member first.", ok=False)
                return
            if not self.selected_book:
                self._set_status("Select a book first.", ok=False)
                return

            with get_conn() as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT issue_id FROM issues
                    WHERE member_id=? AND book_id=? AND status='issued' LIMIT 1
                """, (self.selected_member[0], self.selected_book[0]))
                row = cur.fetchone()
                if not row:
                    self._set_status("No active issued book found.", ok=False)
                    return
                issue_id = row[0]

            return_date = self.return_date_entry.get().strip()
            perform_return(issue_id, return_date)
            self._set_status("✅ Book returned successfully!")

        except Exception as e:
            self._set_status(f"Return failed: {e}", ok=False)
            print("Exception in return_book:", e)
