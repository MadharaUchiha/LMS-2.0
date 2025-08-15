import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from Add_Book import AddBookPage
from issue import IssueBookPage, init_db, seed_sample_data, clear_container
from return_book import ReturnBookPage  # Class-based page

# ---------- Theme ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------- HOME FUNCTION ----------
def show_home_page():
    root = ctk.CTk()
    root.title("LMS - Dashboard")
    root.geometry("1100x650")

    # ---------------- Sidebar ----------------
    sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    main_content_frame = ctk.CTkFrame(root)
    main_content_frame.pack(side="right", fill="both", expand=True)

    title_label = ctk.CTkLabel(sidebar, text="📚 Library LMS", font=("Arial", 20, "bold"))
    title_label.pack(pady=20)

    # ---------- Helper to clear main content ----------
    def clear_main_content():
        clear_container(main_content_frame)

    # ---------- Button Actions ----------
    def add_book():
        clear_main_content()
        page = AddBookPage(main_content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)
    
    def issue_book():
        clear_main_content()
        page = IssueBookPage(main_content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def return_book():
        """Open ReturnBookPage in the main_content_frame"""
        clear_main_content()
        page = ReturnBookPage(main_content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def view_members():
        clear_main_content()
        ctk.CTkLabel(main_content_frame, text="View Members Page (Coming Soon)", font=("Arial", 18, "bold")).pack(pady=20)

    def search_book():
        clear_main_content()
        ctk.CTkLabel(main_content_frame, text="Search Book Page (Coming Soon)", font=("Arial", 18, "bold")).pack(pady=20)

    def logout():
        root.destroy()

    # ---------- Sidebar Buttons ----------
    buttons = [
        ("Add Book", add_book),
        ("Issue Book", issue_book),
        ("Return Book", return_book),
        ("View Members", view_members),
        ("Search Book", search_book),
        ("Logout", logout)
    ]

    for text, cmd in buttons:
        b = ctk.CTkButton(sidebar, text=text, font=("Arial", 14), height=40, command=cmd)
        b.pack(pady=5, padx=20, fill="x")

    # ---------------- Main Dashboard ----------------
    main_frame = ctk.CTkFrame(main_content_frame, fg_color="#1E1E1E")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Stat cards
    stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    stats_frame.pack(fill="x", pady=10)

    stats_data = [
        ("Total Books", "165", "#00FFFF"),
        ("Issued Books", "35", "#FFA500"),
        ("Members", "20", "#00FF00"),
        ("Categories", "5", "#FF69B4"),
    ]

    for title, value, color in stats_data:
        card = ctk.CTkFrame(
            stats_frame, corner_radius=15, fg_color="#2E2E2E", border_width=2, border_color="#3A3A3A", width=150, height=100
        )
        card.pack(side="left", padx=15, pady=5, expand=True, fill="both")

        label_title = ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="#E0E0E0")
        label_title.place(relx=0.5, rely=0.3, anchor="center")
        label_value = ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=color)
        label_value.place(relx=0.5, rely=0.7, anchor="center")

    # Graph
    graph_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#2E2E2E")
    graph_frame.pack(fill="both", expand=True, pady=10, padx=10)

    categories = ['Science', 'Math', 'History', 'Fiction', 'Technology']
    book_counts = [40, 25, 18, 50, 32]
    colors = ['cyan', 'orange', 'pink', 'green', 'purple']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(categories, book_counts, color=colors)
    ax.set_title("Books per Category", fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of Books")

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()


# ----------------------------- MAIN -----------------------------
if __name__ == "__main__":
    # Initialize DB & sample data
    init_db()
    seed_sample_data()

    show_home_page()
