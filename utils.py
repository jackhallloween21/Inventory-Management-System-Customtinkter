import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox


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


def add_graphs(cur, frame, bar_pos=(30, 10), pie_pos=(760, 10)):
    """Render a monthly-earnings bar chart and an order-status pie chart onto *frame*.

    Args:
        cur:     SQLite cursor.
        frame:   Tkinter / CTk parent widget that both chart canvases are placed into.
        bar_pos: (x, y) pixel position for the bar-chart widget relative to *frame*.
        pie_pos: (x, y) pixel position for the pie-chart widget relative to *frame*.
    """
    _BG = '#131325'   # matches the card colour in the new palette
    _FG = '#E8E8F0'   # light text
    _DIM = '#7A7A9A'  # dim text

    plt.style.use('dark_background')
    for param in ('text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color'):
        plt.rcParams[param] = _FG
    for param in ('figure.facecolor', 'axes.facecolor', 'savefig.facecolor'):
        plt.rcParams[param] = _BG

    colors = [
        '#6C63FF', '#00D4AA', '#FFB347', '#FF6B6B',
        '#64BFFF', '#A652BB', '#51E898', '#FFD500', '#FF7A5A', '#8ED1FC',
    ]

    # ── Pie: order status breakdown ──────────────────────────
    try:
        cur.execute(
            'SELECT payment_status, COUNT(*) AS count FROM orders GROUP BY payment_status;'
        )
        payments = cur.fetchall()
        labels  = [x[0].title() for x in payments]
        counts  = [x[1]          for x in payments]

        fig = plt.Figure(figsize=(3.0, 2.6), dpi=100)
        fig.patch.set_facecolor(_BG)
        ax = fig.add_subplot(1, 1, 1)
        if counts:
            ax.pie(counts, labels=labels, autopct='%1.0f%%',
                   colors=colors[:len(labels)], startangle=90,
                   textprops={'fontsize': 8, 'color': _FG})
        else:
            ax.text(0.5, 0.5, 'No orders yet', horizontalalignment='center',
                    verticalalignment='center', color=_DIM, fontsize=9)
        ax.set_title('Order Status Breakdown', color=_FG, fontsize=10, pad=8, fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().place(x=pie_pos[0], y=pie_pos[1])
    except Exception as exc:
        print(f'Error creating pie chart: {exc}')

    # ── Bar: monthly revenue ──────────────────────────────────
    try:
        fig = plt.Figure(figsize=(6.2, 2.6), dpi=100)
        fig.patch.set_facecolor(_BG)
        ax = fig.add_subplot(1, 1, 1)

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

        ax.bar(months, earnings, color='#6C63FF', width=0.6, edgecolor='none')
        ax.set_xlabel('Month',       fontsize=8,  color=_DIM)
        ax.set_ylabel('Revenue',     fontsize=8,  color=_DIM)
        ax.set_title('Monthly Revenue Trend', color=_FG, fontsize=10, pad=8, fontweight='bold')
        ax.tick_params(axis='both', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1C1C35')
        ax.spines['bottom'].set_color('#1C1C35')
        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().place(x=bar_pos[0], y=bar_pos[1])
    except Exception as exc:
        print(f'Error creating bar chart: {exc}')