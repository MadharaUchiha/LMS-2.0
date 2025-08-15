import customtkinter as ctk
import tkinter as tk
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading

from Add_Book import AddBookPage
from issue import IssueBookPage, init_db, seed_sample_data, clear_container
from return_book import ReturnBookPage
from view_members import show_view_members_page



def show_home_page_popup(app):
    """
    Opens the Home/Dashboard in a popup with loading animation.
    """
    popup = ctk.CTkToplevel(app)
    popup.geometry("1100x650")
    popup.title("LMS - Home")
    popup.transient(app)
    popup.grab_set()

    container = ctk.CTkFrame(popup)
    container.pack(fill="both", expand=True)

    # Loading Screen
    loading_frame = ctk.CTkFrame(container)
    loading_frame.pack(fill="both", expand=True)
    loading_label = ctk.CTkLabel(
        loading_frame, text="Loading Dashboard...",
        font=("Arial", 22, "bold")
    )
    loading_label.pack(expand=True)

    progress = ctk.CTkProgressBar(loading_frame, mode="indeterminate")
    progress.pack(pady=20)
    progress.start()

    def load_dashboard():
        time.sleep(2)  # simulate loading delay
        loading_frame.destroy()
        show_home_page(popup, container)

    threading.Thread(target=load_dashboard, daemon=True).start()


def show_home_page(app, container):
    """
    Renders the Home/Dashboard INSIDE the given container.
    """
    init_db()
    seed_sample_data()

    clear_container(container)

    root_frame = ctk.CTkFrame(container, fg_color="transparent")
    root_frame.pack(fill="both", expand=True)

    sidebar = ctk.CTkFrame(root_frame, width=220, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    content_frame = ctk.CTkFrame(root_frame, fg_color="#1E1E1E")
    content_frame.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(sidebar, text="📚 Library LMS", font=("Arial", 20, "bold")).pack(pady=20)

    def clear_main():
        clear_container(content_frame)

    def render_dashboard():
        clear_main()
        main_frame = ctk.CTkFrame(content_frame, fg_color="#1E1E1E")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Stats cards section (Responsive) ---
        stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)

        stats_data = [
            ("Total Books", "165", "#00FFFF"),
            ("Issued Books", "35", "#FFA500"),
            ("Members", "20", "#00FF00"),
            ("Categories", "5", "#FF69B4"),
        ]

        # Configure columns for equal expansion
        for i in range(len(stats_data)):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="statcol")

        for col, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                corner_radius=15,
                fg_color="#2E2E2E",
                border_width=2,
                border_color="#3A3A3A",
                height=100
            )
            card.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"),
                         text_color="#E0E0E0").pack(pady=(15, 0))
            ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"),
                         text_color=color).pack(pady=(5, 0))

        # --- Graph section ---
        graph_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#2E2E2E")
        graph_frame.pack(fill="both", expand=True, pady=10, padx=10)

        categories = ['Science', 'Math', 'History', 'Fiction', 'Technology']
        book_counts = [40, 25, 18, 50, 32]
        colors = ['cyan', 'orange', 'pink', 'green', 'purple']

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(categories, book_counts, color=colors)
        ax.set_title("Books per Category", fontsize=14, fontweight="bold")
        ax.set_ylabel("Number of Books")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- Other page renderers ---
    def add_book():
        clear_main()
        page = AddBookPage(content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def issue_book():
        clear_main()
        page = IssueBookPage(content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def return_book():
        clear_main()
        page = ReturnBookPage(content_frame)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def view_members():
        show_view_members_page(content_frame)

    def search_book():
        clear_main()
        ctk.CTkLabel(content_frame, text="Search Book Page (Coming Soon)",
                     font=("Arial", 18, "bold")).pack(pady=20)
    def logout():
    # Clear the current container and show the login page
        clear_container(container)  # clear current home/dashboard
        app.show_login()  # show the login page



    # Sidebar buttons
    buttons = [
        ("Home", render_dashboard),
        ("Add Book", add_book),
        ("Issue Book", issue_book),
        ("Return Book", return_book),
        ("View Members", view_members),
        ("Search Book", search_book),
        ("Logout", logout),
    ]
    for text, cmd in buttons:
        ctk.CTkButton(sidebar, text=text, font=("Arial", 14),
                      height=40, command=cmd).pack(pady=5, padx=20, fill="x")

    render_dashboard()
