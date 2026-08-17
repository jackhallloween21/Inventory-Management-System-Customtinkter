import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import customtkinter as ctk


def resource_path(relative_path):
    """Return the absolute path to a bundled resource.

    When running as a PyInstaller --onefile executable, assets are
    extracted to a temporary folder stored in sys._MEIPASS.  When
    running directly from source the project root (the directory that
    contains this file) is used instead.
    """
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def error(text):
    """Creates an error message box and prints the error."""
    print(f'[!]   {text}!')
    messagebox.showerror('[ Error ]', text)


def add_graphs(cur, frame, bar_pos=None, pie_pos=None):
    """Render a monthly-earnings bar chart and an order-status pie chart onto *frame*.

    Args:
        cur:     SQLite cursor.
        frame:   Tkinter / CTk parent widget that both chart canvases are placed into.
        bar_pos: Optional (x, y) pixel position (kept for backwards compatibility).
        pie_pos: Optional (x, y) pixel position (kept for backwards compatibility).
    """
    _BG = '#131325'   # matches the card colour in the modern palette
    _FG = '#E8E8F0'   # light text
    _DIM = '#9A9AB8'  # dim text with improved contrast

    plt.style.use('dark_background')
    for param in ('text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color'):
        plt.rcParams[param] = _FG
    for param in ('figure.facecolor', 'axes.facecolor', 'savefig.facecolor'):
        plt.rcParams[param] = _BG

    colors = [
        '#6C63FF', '#00D4AA', '#FFB347', '#FF6B6B',
        '#64BFFF', '#A652BB', '#51E898', '#FFD500', '#FF7A5A', '#8ED1FC',
    ]

    for child in frame.winfo_children():
        child.destroy()

    bar_container = ctk.CTkFrame(frame, fg_color="transparent")
    bar_container.pack(side="left", fill="both", expand=True, padx=(15, 10), pady=10)

    pie_container = ctk.CTkFrame(frame, fg_color="transparent")
    pie_container.pack(side="right", fill="both", expand=True, padx=(10, 15), pady=10)

    # ── Bar: monthly revenue ──────────────────────────────────
    try:
        fig_bar = plt.Figure(figsize=(7.5, 3.4), dpi=100)
        fig_bar.patch.set_facecolor(_BG)
        ax_bar = fig_bar.add_subplot(1, 1, 1)

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        cur.execute(
            "SELECT strftime('%m', o.date) AS month, "
            "       SUM(oi.quantity * oi.price) AS earnings "
            "FROM orders o "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "WHERE LOWER(o.payment_status) = 'paid' "
            "  AND strftime('%Y', o.date) = strftime('%Y', 'now') "
            "GROUP BY month ORDER BY month;"
        )
        earnings = [0] * 12
        for month, amt in cur.fetchall():
            earnings[int(month) - 1] = amt

        ax_bar.bar(months, earnings, color='#6C63FF', width=0.55, edgecolor='none')
        ax_bar.set_xlabel('Month', fontsize=11, color=_DIM, labelpad=6, fontweight='bold')
        ax_bar.set_ylabel('Revenue (₹)', fontsize=11, color=_DIM, labelpad=6, fontweight='bold')
        ax_bar.set_title('Monthly Revenue Trend', color=_FG, fontsize=14, pad=12, fontweight='bold')
        ax_bar.tick_params(axis='both', labelsize=10, colors=_FG)
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.spines['left'].set_color('#2A2A48')
        ax_bar.spines['bottom'].set_color('#2A2A48')
        ax_bar.grid(axis='y', linestyle='--', alpha=0.15, color='#E8E8F0')
        fig_bar.tight_layout(pad=1.5)

        canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_container)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(fill="both", expand=True)
    except Exception as exc:
        print(f'Error creating bar chart: {exc}')

    # ── Pie: order status breakdown ──────────────────────────
    try:
        cur.execute(
            'SELECT payment_status, COUNT(*) AS count FROM orders GROUP BY payment_status;'
        )
        payments = cur.fetchall()
        labels  = [x[0].title() for x in payments]
        counts  = [x[1]          for x in payments]

        fig_pie = plt.Figure(figsize=(4.5, 3.4), dpi=100)
        fig_pie.patch.set_facecolor(_BG)
        ax_pie = fig_pie.add_subplot(1, 1, 1)
        if counts:
            wedges, texts, autotexts = ax_pie.pie(
                counts, labels=labels, autopct='%1.0f%%',
                colors=colors[:len(labels)], startangle=90,
                textprops={'fontsize': 11, 'color': _FG, 'fontweight': 'bold'},
                pctdistance=0.65
            )
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_color('#FFFFFF')
                autotext.set_weight('bold')
        else:
            ax_pie.text(0.5, 0.5, 'No orders yet', horizontalalignment='center',
                        verticalalignment='center', color=_DIM, fontsize=12, fontweight='bold')
        ax_pie.set_title('Order Status Breakdown', color=_FG, fontsize=14, pad=12, fontweight='bold')
        fig_pie.tight_layout(pad=1.5)

        canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_container)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True)
    except Exception as exc:
        print(f'Error creating pie chart: {exc}')