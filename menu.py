import os
import sys
import csv
import tkinter
from tkinter import ttk, messagebox, filedialog
from datetime import date
import customtkinter as ctk
from PIL import Image

from utils import error, add_graphs, resource_path

# Design System Color Palette
BG_COLOR = "#08080F"
SIDEBAR_COLOR = "#0C0C1A"
CARD_COLOR = "#131325"
CARD_ALT_COLOR = "#1C1C35"
PRIMARY_COLOR = "#6C63FF"
PRIMARY_HOVER = "#5850DD"
SECONDARY_COLOR = "#00D4AA"
DANGER_COLOR = "#FF6B6B"
WARNING_COLOR = "#FFB347"
TEXT_COLOR = "#E8E8F0"
TEXT_DIM_COLOR = "#7A7A9A"
FONT_FAMILY = "Segoe UI"


class Menu:
    """Represents the main dashboard and menu interface of InvenTrack."""

    def __init__(self, con, user, login_win):
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("dark")

        self.login_win = login_win
        self.window = ctk.CTkToplevel(self.login_win)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        self.window.configure(fg_color=BG_COLOR)

        self.con = con
        self.cur = con.cursor()
        self.user = user  # (username, password, account_type)
        self.font = FONT_FAMILY
        self.logout = False
        self.nav_buttons = {}
        self.current_section = None

        self.make_window()

    def logout(self):
        """Handles logout and cleanup."""
        self.logout = True
        try:
            self.window.destroy()
            self.login_win.destroy()
            self.con.close()
        except Exception:
            pass

    def make_window(self):
        """Sets up main window dimensions and split layout."""
        width = 1350
        height = 750
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = max(0, int((screen_width / 2) - (width / 2)))
        y = max(0, int((screen_height / 2) - (height / 2)))
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.login_win.withdraw()
        self.window.resizable(False, False)

        # Main Layout: Sidebar (220px) + Main Content Area
        self.make_panel()

    def make_panel(self):
        """Creates sidebar navigation and main content container."""
        # ── Sidebar Panel ─────────────────────────────────────────
        self.side_panel = ctk.CTkFrame(
            self.window, width=220, corner_radius=0, fg_color=SIDEBAR_COLOR
        )
        self.side_panel.pack(side="left", fill="y")
        self.side_panel.pack_propagate(False)

        # App Logo & Branding Header
        brand_frame = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(25, 30))

        logo_lbl = ctk.CTkLabel(
            brand_frame, text="📦", font=(self.font, 28)
        )
        logo_lbl.pack(side="left", padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            brand_frame, text="InvenTrack", font=(self.font, 20, "bold"), text_color=TEXT_COLOR
        )
        title_lbl.pack(side="left")

        # Determine sections based on user role
        if self.user[2] == "ADMIN":
            sections = [
                ("dashboard", "Dashboard"),
                ("inventory", "Inventory"),
                ("orders", "Orders"),
                ("users", "Users"),
            ]
        else:
            sections = [
                ("dashboard", "Dashboard"),
                ("inventory", "Inventory"),
                ("shop", "Shop"),
                ("history", "History"),
            ]

        section_callbacks = {
            "dashboard": self.dashboard,
            "inventory": self.inventory,
            "orders": self.orders,
            "users": self.users,
            "shop": self.shop,
            "history": self.history,
        }

        # Navigation Buttons
        nav_container = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        nav_container.pack(fill="x", expand=True, anchor="n", padx=10)

        for sec_id, sec_label in sections:
            btn_frame = ctk.CTkFrame(nav_container, fg_color="transparent", height=45)
            btn_frame.pack(fill="x", pady=4)
            btn_frame.pack_propagate(False)

            # Active highlight bar indicator on left side
            indicator = ctk.CTkFrame(
                btn_frame, width=4, corner_radius=2, fg_color="transparent"
            )
            indicator.pack(side="left", fill="y", padx=(0, 6))

            # Icon image if available
            img_path = resource_path(f"imgs/{sec_id}.png")
            img = None
            if os.path.exists(img_path):
                try:
                    img = ctk.CTkImage(Image.open(img_path).resize((20, 20)), size=(20, 20))
                except Exception:
                    img = None

            btn = ctk.CTkButton(
                btn_frame,
                text=f"  {sec_label}",
                image=img,
                compound="left",
                anchor="w",
                font=(self.font, 14, "bold"),
                fg_color="transparent",
                text_color=TEXT_DIM_COLOR,
                hover_color=CARD_COLOR,
                height=40,
                corner_radius=8,
                command=section_callbacks[sec_id],
            )
            btn.pack(side="left", fill="both", expand=True)
            self.nav_buttons[sec_id] = (btn, indicator)

        # Bottom Section: User Profile Card & Logout Button
        bottom_frame = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=20)

        # User Badge Card
        user_card = ctk.CTkFrame(bottom_frame, fg_color=CARD_COLOR, corner_radius=10, height=55)
        user_card.pack(fill="x", pady=(0, 12))
        user_card.pack_propagate(False)

        user_icon = ctk.CTkLabel(user_card, text="👤", font=(self.font, 18))
        user_icon.pack(side="left", padx=(12, 8))

        user_info = ctk.CTkFrame(user_card, fg_color="transparent")
        user_info.pack(side="left", fill="both", expand=True, pady=8)

        uname_lbl = ctk.CTkLabel(
            user_info,
            text=self.user[0],
            font=(self.font, 12, "bold"),
            text_color=TEXT_COLOR,
            anchor="w",
        )
        uname_lbl.pack(anchor="w")

        role_badge = ctk.CTkLabel(
            user_info,
            text=self.user[2],
            font=(self.font, 9, "bold"),
            text_color=SECONDARY_COLOR if self.user[2] == "ADMIN" else PRIMARY_COLOR,
            anchor="w",
        )
        role_badge.pack(anchor="w")

        # Logout Button
        logout_img_path = resource_path("imgs/logout.png")
        logout_img = None
        if os.path.exists(logout_img_path):
            try:
                logout_img = ctk.CTkImage(Image.open(logout_img_path).resize((18, 18)), size=(18, 18))
            except Exception:
                logout_img = None

        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="  Log Out",
            image=logout_img,
            compound="left",
            anchor="w",
            font=(self.font, 13, "bold"),
            fg_color="transparent",
            text_color=DANGER_COLOR,
            hover_color="#2A161A",
            height=38,
            corner_radius=8,
            command=self.logout,
        )
        logout_btn.pack(fill="x")

        # ── Main Content Area Panel ────────────────────────────────
        self.frame = ctk.CTkFrame(
            self.window, corner_radius=0, fg_color=BG_COLOR
        )
        self.frame.pack(side="left", fill="both", expand=True)

        self.dashboard()

    def _clear_content(self, section_name):
        """Clears content area and updates active navigation indicator."""
        self.current_section = section_name
        for child in self.frame.winfo_children():
            child.destroy()

        # Update sidebar nav styling
        for sec_id, (btn, indicator) in self.nav_buttons.items():
            if sec_id == section_name:
                btn.configure(fg_color=CARD_COLOR, text_color=TEXT_COLOR)
                indicator.configure(fg_color=PRIMARY_COLOR)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_DIM_COLOR)
                indicator.configure(fg_color="transparent")

    def _create_header(self, title, subtitle=None):
        """Creates a standardized view header bar."""
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        title_lbl = ctk.CTkLabel(
            header_frame, text=title, font=(self.font, 24, "bold"), text_color=TEXT_COLOR
        )
        title_lbl.pack(anchor="w")

        if subtitle:
            sub_lbl = ctk.CTkLabel(
                header_frame, text=subtitle, font=(self.font, 12), text_color=TEXT_DIM_COLOR
            )
            sub_lbl.pack(anchor="w")

        return header_frame

    def _dialog(self, title, width=500, height=480):
        """Creates a standardized modal dialog window."""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.configure(fg_color=CARD_COLOR)
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        # Center dialog relative to main window
        wx = self.window.winfo_x()
        wy = self.window.winfo_y()
        ww = self.window.winfo_width()
        wh = self.window.winfo_height()
        cx = wx + max(0, (ww - width) // 2)
        cy = wy + max(0, (wh - height) // 2)
        dialog.geometry(f"{width}x{height}+{cx}+{cy}")

        return dialog

    def _export_csv(self, tree, filename_prefix="export"):
        """Exports Treeview content to a CSV file."""
        columns = [tree.heading(col)["text"] for col in tree["columns"]]
        rows = [tree.item(item)["values"] for item in tree.get_children()]

        if not rows:
            error("No data available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{filename_prefix}_{date.today()}.csv",
            title="Export Data to CSV",
        )

        if filepath:
            try:
                with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
                messagebox.showinfo("Export Successful", f"Data exported successfully to:\n{filepath}")
            except Exception as e:
                error(f"Failed to export CSV: {e}")

    # ── 1. DASHBOARD VIEW ──────────────────────────────────────────
    def dashboard(self):
        """Displays the modernized dashboard with cards, alerts, graphs, and recent orders."""
        self._clear_content("dashboard")
        self.window.title("InvenTrack - Dashboard")
        self._create_header("Dashboard", "System overview, analytics, and alerts")

        # ── Stat Cards ────────────────────────────────────────────
        self.cur.execute(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE date(date) = date('now') AND LOWER(payment_status)='paid';"
        )
        sales_today_amt = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM orders;")
        total_orders = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM products;")
        total_products = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM products WHERE quantity < 10;")
        low_stock_count = self.cur.fetchone()[0]

        self.cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE LOWER(payment_status)='paid';")
        total_revenue = self.cur.fetchone()[0]

        cards_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 15))

        metrics = [
            ("Sales Today", f"₹{sales_today_amt:,.2f}", "📅", SECONDARY_COLOR),
            ("Total Revenue", f"₹{total_revenue:,.2f}", "💰", PRIMARY_COLOR),
            ("Total Orders", f"{total_orders:,}", "📦", "#64BFFF"),
            ("Low Stock Items", f"{low_stock_count}", "⚠️", DANGER_COLOR if low_stock_count > 0 else SECONDARY_COLOR),
        ]

        for title, val, icon, color in metrics:
            card = ctk.CTkFrame(cards_frame, fg_color=CARD_COLOR, corner_radius=12, height=95)
            card.pack(side="left", fill="both", expand=True, padx=6)
            card.pack_propagate(False)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(12, 0))

            lbl_title = ctk.CTkLabel(
                top_row, text=title, font=(self.font, 12, "bold"), text_color=TEXT_DIM_COLOR
            )
            lbl_title.pack(side="left")

            lbl_icon = ctk.CTkLabel(top_row, text=icon, font=(self.font, 16))
            lbl_icon.pack(side="right")

            lbl_val = ctk.CTkLabel(
                card, text=val, font=(self.font, 20, "bold"), text_color=color
            )
            lbl_val.pack(anchor="w", padx=16, pady=(4, 0))

        # ── Low Stock Alert Banner (If items < 10 exist) ─────────
        if low_stock_count > 0:
            self.cur.execute("SELECT product_name, quantity FROM products WHERE quantity < 10 LIMIT 5;")
            low_items = self.cur.fetchall()
            alert_text = "  |  ".join([f"{name} ({qty} left)" for name, qty in low_items])

            alert_strip = ctk.CTkFrame(
                self.frame, fg_color="#2D1519", border_color=DANGER_COLOR, border_width=1, corner_radius=8, height=36
            )
            alert_strip.pack(fill="x", padx=36, pady=(0, 15))
            alert_strip.pack_propagate(False)

            a_icon = ctk.CTkLabel(
                alert_strip, text=" ⚠️ LOW STOCK ALERT: ", font=(self.font, 11, "bold"), text_color=DANGER_COLOR
            )
            a_icon.pack(side="left", padx=(12, 0))

            a_msg = ctk.CTkLabel(
                alert_strip, text=alert_text, font=(self.font, 11), text_color=TEXT_COLOR
            )
            a_msg.pack(side="left", padx=5)

        # ── Lower Section: Embedded Charts + Recent Orders ────────
        lower_box = ctk.CTkFrame(self.frame, fg_color="transparent")
        lower_box.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Chart Container Card (Left / Top)
        chart_card = ctk.CTkFrame(lower_box, fg_color=CARD_COLOR, corner_radius=12, height=300)
        chart_card.pack(fill="x", pady=(0, 15))
        chart_card.pack_propagate(False)

        try:
            add_graphs(self.cur, chart_card, bar_pos=(15, 10), pie_pos=(660, 10))
        except Exception as e:
            print(f"Error rendering graphs: {e}")

        # Recent Orders Quick View (Bottom)
        recent_card = ctk.CTkFrame(lower_box, fg_color=CARD_COLOR, corner_radius=12)
        recent_card.pack(fill="both", expand=True)

        recent_header = ctk.CTkFrame(recent_card, fg_color="transparent")
        recent_header.pack(fill="x", padx=16, pady=(10, 5))

        r_title = ctk.CTkLabel(
            recent_header, text="Recent Orders", font=(self.font, 14, "bold"), text_color=TEXT_COLOR
        )
        r_title.pack(side="left")

        # Treeview for Recent Orders
        tree_frame = ctk.CTkFrame(recent_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.make_table(
            tree_frame,
            ("Order ID", "Customer", "Date", "Items", "Amount", "Status"),
            [100, 180, 120, 100, 140, 140],
            height=130,
        )

        self.cur.execute(
            "SELECT order_id, customer, date, total_items, total_amount, payment_status FROM orders ORDER BY order_id DESC LIMIT 5;"
        )
        rows = self.cur.fetchall()
        for r in rows:
            formatted_row = (r[0], r[1], r[2], r[3], f"₹{r[4]:,.2f}", str(r[5]).title())
            tag = "paid" if str(r[5]).lower() == "paid" else "pending"
            self.tree.insert("", "end", values=formatted_row, tags=(tag,))

    # ── 2. INVENTORY VIEW ──────────────────────────────────────────
    def inventory(self):
        """Displays Inventory products with search, low-stock filter, Add/Edit/Delete, and CSV export."""
        self._clear_content("inventory")
        self.window.title("InvenTrack - Inventory Management")
        self._create_header("Inventory", "Manage stock products, update pricing and quantities")

        # Toolbar Frame
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 15))

        # Search Bar
        self.inv_search_var = ctk.StringVar()
        self.inv_search_var.trace_add("write", lambda *args: self._filter_inventory())

        search_entry = ctk.CTkEntry(
            toolbar,
            width=280,
            height=36,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            text_color=TEXT_COLOR,
            placeholder_text="🔍  Search product ID, name...",
            textvariable=self.inv_search_var,
        )
        search_entry.pack(side="left", padx=(0, 15))

        # Low Stock Filter Checkbox
        self.low_stock_filter_var = ctk.BooleanVar(value=False)
        chk_low = ctk.CTkCheckBox(
            toolbar,
            text="Low Stock Only (<10)",
            font=(self.font, 12),
            text_color=TEXT_COLOR,
            variable=self.low_stock_filter_var,
            command=self._filter_inventory,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
        )
        chk_low.pack(side="left", padx=(0, 15))

        # Admin Action Buttons
        if self.user[2] == "ADMIN":
            btn_add = ctk.CTkButton(
                toolbar,
                text="+ Add Product",
                font=(self.font, 12, "bold"),
                fg_color=PRIMARY_COLOR,
                hover_color=PRIMARY_HOVER,
                height=36,
                command=self.add_product_dialog,
            )
            btn_add.pack(side="left", padx=(0, 8))

            btn_edit = ctk.CTkButton(
                toolbar,
                text="✏️ Edit",
                font=(self.font, 12, "bold"),
                fg_color=CARD_ALT_COLOR,
                hover_color="#2A2A48",
                height=36,
                command=self.edit_product_dialog,
            )
            btn_edit.pack(side="left", padx=(0, 8))

            btn_del = ctk.CTkButton(
                toolbar,
                text="🗑️ Delete",
                font=(self.font, 12, "bold"),
                fg_color="#3D1A22",
                hover_color="#581F2C",
                text_color=DANGER_COLOR,
                height=36,
                command=self.delete_product,
            )
            btn_del.pack(side="left", padx=(0, 8))

        # Export CSV Button
        btn_csv = ctk.CTkButton(
            toolbar,
            text="📥 Export CSV",
            font=(self.font, 12, "bold"),
            fg_color=CARD_ALT_COLOR,
            hover_color="#2A2A48",
            height=36,
            command=lambda: self._export_csv(self.tree, "inventory"),
        )
        btn_csv.pack(side="right")

        # Inventory Table Container
        tbl_container = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12)
        tbl_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        headings = ("Product ID", "Product Name", "Description", "Price", "Quantity")
        widths = [140, 250, 380, 140, 140]
        self.make_table(tbl_container, headings, widths)
        self._filter_inventory()

    def _filter_inventory(self):
        """Populates inventory table filtered by search entry and low stock check."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query_str = self.inv_search_var.get().strip().lower()
        low_only = self.low_stock_filter_var.get()

        self.cur.execute("SELECT product_id, product_name, description, price, quantity FROM products;")
        products = self.cur.fetchall()

        for p in products:
            p_id, p_name, p_desc, p_price, p_qty = p
            if low_only and p_qty >= 10:
                continue

            if query_str:
                match = (
                    query_str in str(p_id).lower()
                    or query_str in str(p_name).lower()
                    or query_str in str(p_desc).lower()
                )
                if not match:
                    continue

            tag = "low_stock" if p_qty < 10 else "normal"
            formatted = (p_id, p_name, p_desc, f"₹{p_price:,.2f}", p_qty)
            self.tree.insert("", "end", values=formatted, tags=(tag,))

    def add_product_dialog(self):
        """Dialog to add a new inventory product."""
        dlg = self._dialog("Add New Product", width=460, height=480)

        lbl_t = ctk.CTkLabel(dlg, text="Add New Product", font=(self.font, 18, "bold"), text_color=TEXT_COLOR)
        lbl_t.place(x=30, y=20)

        fields = [
            ("Product ID", "e.g. P101"),
            ("Product Name", "e.g. Wireless Mouse"),
            ("Description", "Brief product description"),
            ("Price (₹)", "e.g. 499.00"),
            ("Quantity", "e.g. 50"),
        ]

        entries = {}
        y = 65
        for label, placeholder in fields:
            lbl = ctk.CTkLabel(dlg, text=label, font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
            lbl.place(x=30, y=y)

            ent = ctk.CTkEntry(
                dlg,
                width=400,
                height=36,
                corner_radius=8,
                fg_color=CARD_ALT_COLOR,
                border_color="#2A2A45",
                text_color=TEXT_COLOR,
                placeholder_text=placeholder,
            )
            ent.place(x=30, y=y + 22)
            entries[label] = ent
            y += 68

        def submit():
            p_id = entries["Product ID"].get().strip()
            p_name = entries["Product Name"].get().strip()
            p_desc = entries["Description"].get().strip()
            p_price_str = entries["Price (₹)"].get().strip()
            p_qty_str = entries["Quantity"].get().strip()

            if not all([p_id, p_name, p_desc, p_price_str, p_qty_str]):
                error("All fields are required.")
                return

            try:
                p_price = float(p_price_str)
                p_qty = int(p_qty_str)
                if p_price < 0 or p_qty < 0:
                    error("Price and Quantity must be non-negative.")
                    return
            except ValueError:
                error("Invalid Price or Quantity number format.")
                return

            self.cur.execute("SELECT * FROM products WHERE product_id=?", (p_id,))
            if self.cur.fetchone():
                error("Product ID already exists.")
                return

            self.cur.execute(
                "INSERT INTO products (product_id, product_name, description, price, quantity) VALUES (?, ?, ?, ?, ?)",
                (p_id, p_name, p_desc, p_price, p_qty),
            )
            self.con.commit()
            messagebox.showinfo("Success", f"Product '{p_name}' added successfully!")
            dlg.destroy()
            self._filter_inventory()

        btn_save = ctk.CTkButton(
            dlg,
            text="Save Product",
            font=(self.font, 13, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            width=400,
            height=40,
            command=submit,
        )
        btn_save.place(x=30, y=415)

    def edit_product_dialog(self):
        """Dialog to edit the selected inventory product."""
        sel = self.tree.selection()
        if not sel:
            error("Please select a product to edit.")
            return

        values = self.tree.item(sel[0], "values")
        p_id = values[0]

        self.cur.execute("SELECT product_id, product_name, description, price, quantity FROM products WHERE product_id=?", (p_id,))
        prod = self.cur.fetchone()
        if not prod:
            error("Selected product not found.")
            return

        dlg = self._dialog(f"Edit Product - {p_id}", width=460, height=480)

        lbl_t = ctk.CTkLabel(dlg, text=f"Edit Product ({p_id})", font=(self.font, 18, "bold"), text_color=TEXT_COLOR)
        lbl_t.place(x=30, y=20)

        fields = [
            ("Product Name", prod[1]),
            ("Description", prod[2]),
            ("Price (₹)", str(prod[3])),
            ("Quantity", str(prod[4])),
        ]

        entries = {}
        y = 65
        for label, default_val in fields:
            lbl = ctk.CTkLabel(dlg, text=label, font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
            lbl.place(x=30, y=y)

            ent = ctk.CTkEntry(
                dlg,
                width=400,
                height=36,
                corner_radius=8,
                fg_color=CARD_ALT_COLOR,
                border_color="#2A2A45",
                text_color=TEXT_COLOR,
            )
            ent.insert(0, default_val)
            ent.place(x=30, y=y + 22)
            entries[label] = ent
            y += 75

        def submit():
            p_name = entries["Product Name"].get().strip()
            p_desc = entries["Description"].get().strip()
            p_price_str = entries["Price (₹)"].get().strip()
            p_qty_str = entries["Quantity"].get().strip()

            if not all([p_name, p_desc, p_price_str, p_qty_str]):
                error("All fields are required.")
                return

            try:
                p_price = float(p_price_str)
                p_qty = int(p_qty_str)
                if p_price < 0 or p_qty < 0:
                    error("Price and Quantity must be non-negative.")
                    return
            except ValueError:
                error("Invalid Price or Quantity number format.")
                return

            self.cur.execute(
                "UPDATE products SET product_name=?, description=?, price=?, quantity=? WHERE product_id=?",
                (p_name, p_desc, p_price, p_qty, p_id),
            )
            self.con.commit()
            messagebox.showinfo("Success", f"Product '{p_id}' updated successfully!")
            dlg.destroy()
            self._filter_inventory()

        btn_update = ctk.CTkButton(
            dlg,
            text="Update Product",
            font=(self.font, 13, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            width=400,
            height=40,
            command=submit,
        )
        btn_update.place(x=30, y=400)

    def delete_product(self):
        """Deletes selected product after user confirmation."""
        sel = self.tree.selection()
        if not sel:
            error("Please select a product to delete.")
            return

        values = self.tree.item(sel[0], "values")
        p_id, p_name = values[0], values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{p_name}' ({p_id})?"):
            self.cur.execute("DELETE FROM products WHERE product_id=?", (p_id,))
            self.con.commit()
            messagebox.showinfo("Deleted", f"Product '{p_name}' deleted.")
            self._filter_inventory()

    # ── 3. ORDERS VIEW ─────────────────────────────────────────────
    def orders(self):
        """Displays orders list with live search, payment status toggles, and CSV export."""
        self._clear_content("orders")
        self.window.title("InvenTrack - Customer Orders")
        self._create_header("Orders", "View transactions, update payment status, and export records")

        # Toolbar
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 15))

        self.ord_search_var = ctk.StringVar()
        self.ord_search_var.trace_add("write", lambda *args: self._filter_orders())

        search_entry = ctk.CTkEntry(
            toolbar,
            width=300,
            height=36,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            text_color=TEXT_COLOR,
            placeholder_text="🔍  Search order ID, customer, status...",
            textvariable=self.ord_search_var,
        )
        search_entry.pack(side="left", padx=(0, 15))

        # Status Action Buttons
        btn_paid = ctk.CTkButton(
            toolbar,
            text="✓ Mark Paid",
            font=(self.font, 12, "bold"),
            fg_color="#13382D",
            hover_color="#1B5242",
            text_color=SECONDARY_COLOR,
            height=36,
            command=lambda: self.mark_order_status("paid"),
        )
        btn_paid.pack(side="left", padx=(0, 8))

        btn_pending = ctk.CTkButton(
            toolbar,
            text="⏳ Mark Pending",
            font=(self.font, 12, "bold"),
            fg_color="#3D2D15",
            hover_color="#58411F",
            text_color=WARNING_COLOR,
            height=36,
            command=lambda: self.mark_order_status("pending"),
        )
        btn_pending.pack(side="left", padx=(0, 8))

        # Export CSV Button
        btn_csv = ctk.CTkButton(
            toolbar,
            text="📥 Export CSV",
            font=(self.font, 12, "bold"),
            fg_color=CARD_ALT_COLOR,
            hover_color="#2A2A48",
            height=36,
            command=lambda: self._export_csv(self.tree, "orders"),
        )
        btn_csv.pack(side="right")

        # Table Container
        tbl_container = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12)
        tbl_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        headings = ("Order ID", "Customer", "Date", "Total Items", "Total Amount", "Payment Status")
        widths = [140, 240, 160, 140, 180, 180]
        self.make_table(tbl_container, headings, widths)
        self._filter_orders()

    def _filter_orders(self):
        """Filters orders table based on search query."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query_str = self.ord_search_var.get().strip().lower()
        self.cur.execute("SELECT order_id, customer, date, total_items, total_amount, payment_status FROM orders ORDER BY order_id DESC;")
        rows = self.cur.fetchall()

        for r in rows:
            o_id, cust, o_date, qty, amt, status = r
            if query_str:
                match = (
                    query_str in str(o_id).lower()
                    or query_str in str(cust).lower()
                    or query_str in str(status).lower()
                    or query_str in str(o_date).lower()
                )
                if not match:
                    continue

            tag = "paid" if str(status).lower() == "paid" else "pending"
            formatted = (o_id, cust, o_date, qty, f"₹{amt:,.2f}", str(status).title())
            self.tree.insert("", "end", values=formatted, tags=(tag,))

    def mark_order_status(self, new_status):
        """Updates payment status of selected order."""
        sel = self.tree.selection()
        if not sel:
            error("Please select an order to update.")
            return

        values = self.tree.item(sel[0], "values")
        order_id = values[0]

        self.cur.execute("UPDATE orders SET payment_status=? WHERE order_id=?", (new_status, order_id))
        self.con.commit()
        messagebox.showinfo("Status Updated", f"Order #{order_id} status marked as '{new_status.title()}'.")
        self._filter_orders()

    # ── 4. USERS VIEW (ADMIN ONLY) ──────────────────────────────────
    def users(self):
        """Displays user accounts list with search and delete user option."""
        self._clear_content("users")
        self.window.title("InvenTrack - User Management")
        self._create_header("User Management", "View and manage registered user accounts")

        # Toolbar
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 15))

        self.usr_search_var = ctk.StringVar()
        self.usr_search_var.trace_add("write", lambda *args: self._filter_users())

        search_entry = ctk.CTkEntry(
            toolbar,
            width=300,
            height=36,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            text_color=TEXT_COLOR,
            placeholder_text="🔍  Search username, account type...",
            textvariable=self.usr_search_var,
        )
        search_entry.pack(side="left", padx=(0, 15))

        btn_del_user = ctk.CTkButton(
            toolbar,
            text="🗑️ Delete User",
            font=(self.font, 12, "bold"),
            fg_color="#3D1A22",
            hover_color="#581F2C",
            text_color=DANGER_COLOR,
            height=36,
            command=self.delete_user,
        )
        btn_del_user.pack(side="left")

        # Table Container
        tbl_container = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12)
        tbl_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        headings = ("Username", "Password (Hashed/Hidden)", "Account Type")
        widths = [300, 400, 300]
        self.make_table(tbl_container, headings, widths)
        self._filter_users()

    def _filter_users(self):
        """Filters users table based on search entry."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query_str = self.usr_search_var.get().strip().lower()
        self.cur.execute("SELECT username, password, account_type FROM users;")
        users = self.cur.fetchall()

        for u in users:
            uname, pwd, acc_type = u
            if query_str:
                if query_str not in uname.lower() and query_str not in acc_type.lower():
                    continue
            masked_pwd = "•" * len(pwd)
            self.tree.insert("", "end", values=(uname, masked_pwd, acc_type))

    def delete_user(self):
        """Deletes selected user account (with safeguards for current user and main Admin)."""
        sel = self.tree.selection()
        if not sel:
            error("Please select a user to delete.")
            return

        values = self.tree.item(sel[0], "values")
        target_username = values[0]

        if target_username == self.user[0]:
            error("You cannot delete your own logged-in account.")
            return

        if target_username.lower() == "admin":
            error("The primary 'Admin' account cannot be deleted.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{target_username}'?"):
            self.cur.execute("DELETE FROM users WHERE username=?", (target_username,))
            self.con.commit()
            messagebox.showinfo("User Deleted", f"User '{target_username}' has been removed.")
            self._filter_users()

    # ── 5. SHOP VIEW (CART & CHECKOUT) ────────────────────────────
    def shop(self):
        """Displays customer shop interface with cart, duplicate item merge, and checkout."""
        self._clear_content("shop")
        self.window.title("InvenTrack - Shop & Cart")
        self._create_header("Shop Items", "Add products to shopping cart and process orders")

        # Action Toolbar
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 15))

        btn_add_cart = ctk.CTkButton(
            toolbar,
            text="+ Add Item to Cart",
            font=(self.font, 12, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            height=36,
            command=self.add_item_dialog,
        )
        btn_add_cart.pack(side="left", padx=(0, 10))

        btn_remove = ctk.CTkButton(
            toolbar,
            text="❌ Remove Selected Item",
            font=(self.font, 12, "bold"),
            fg_color="#3D1A22",
            hover_color="#581F2C",
            text_color=DANGER_COLOR,
            height=36,
            command=self.remove_item_from_cart,
        )
        btn_remove.pack(side="left")

        # Cart Table Container
        tbl_container = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12)
        tbl_container.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        headings = ("Product ID", "Product Name", "Description", "Price", "Quantity", "Total Amount")
        widths = [120, 220, 320, 120, 100, 160]
        self.make_table(tbl_container, headings, widths)

        # Checkout & Running Total Footer Strip
        footer = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12, height=65)
        footer.pack(fill="x", padx=30, pady=(0, 20))
        footer.pack_propagate(False)

        total_title = ctk.CTkLabel(
            footer, text="Total Amount:", font=(self.font, 16, "bold"), text_color=TEXT_DIM_COLOR
        )
        total_title.pack(side="left", padx=(20, 8))

        self.cart_total_lbl = ctk.CTkLabel(
            footer, text="₹0.00", font=(self.font, 22, "bold"), text_color=SECONDARY_COLOR
        )
        self.cart_total_lbl.pack(side="left")

        btn_checkout = ctk.CTkButton(
            footer,
            text="🛍️ Complete Purchase",
            font=(self.font, 14, "bold"),
            fg_color=SECONDARY_COLOR,
            hover_color="#00B38F",
            text_color="#08080F",
            width=220,
            height=42,
            command=self.buy,
        )
        btn_checkout.pack(side="right", padx=20)

    def add_item_dialog(self):
        """Modal dialog to select a product and add to cart with duplicate merging."""
        self.cur.execute("SELECT product_name FROM products WHERE quantity > 0")
        products = [r[0] for r in self.cur.fetchall()]

        if not products:
            error("No items available in stock to purchase.")
            return

        dlg = self._dialog("Add Product to Cart", width=460, height=430)

        lbl_title = ctk.CTkLabel(dlg, text="Select Product to Add", font=(self.font, 18, "bold"), text_color=TEXT_COLOR)
        lbl_title.place(x=30, y=20)

        # Product selection dropdown
        lbl_sel = ctk.CTkLabel(dlg, text="Select Product:", font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
        lbl_sel.place(x=30, y=65)

        self.shop_item_var = ctk.StringVar(value=products[0])

        def on_product_change(choice):
            self.cur.execute("SELECT quantity, price, description, product_id FROM products WHERE product_name=?", (choice,))
            row = self.cur.fetchone()
            if row:
                qty_avail, price, desc, p_id = row
                lbl_stock_val.configure(text=f"{qty_avail} units")
                lbl_price_val.configure(text=f"₹{price:,.2f}")
                lbl_desc_val.configure(text=desc)

        option_menu = ctk.CTkOptionMenu(
            dlg,
            values=products,
            variable=self.shop_item_var,
            command=on_product_change,
            width=400,
            height=36,
            fg_color=CARD_ALT_COLOR,
            button_color=PRIMARY_COLOR,
            button_hover_color=PRIMARY_HOVER,
            dropdown_fg_color=CARD_ALT_COLOR,
        )
        option_menu.place(x=30, y=88)

        # Product Info Preview Frame
        preview_box = ctk.CTkFrame(dlg, fg_color=CARD_ALT_COLOR, corner_radius=10, width=400, height=110)
        preview_box.place(x=30, y=140)
        preview_box.pack_propagate(False)

        lbl_desc_title = ctk.CTkLabel(preview_box, text="Description:", font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
        lbl_desc_title.place(x=15, y=10)
        lbl_desc_val = ctk.CTkLabel(preview_box, text="", font=(self.font, 11), text_color=TEXT_COLOR, anchor="w")
        lbl_desc_val.place(x=100, y=10)

        lbl_stock_title = ctk.CTkLabel(preview_box, text="Stock Avail:", font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
        lbl_stock_title.place(x=15, y=40)
        lbl_stock_val = ctk.CTkLabel(preview_box, text="", font=(self.font, 12, "bold"), text_color=SECONDARY_COLOR)
        lbl_stock_val.place(x=100, y=40)

        lbl_price_title = ctk.CTkLabel(preview_box, text="Unit Price:", font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
        lbl_price_title.place(x=15, y=70)
        lbl_price_val = ctk.CTkLabel(preview_box, text="", font=(self.font, 12, "bold"), text_color=PRIMARY_COLOR)
        lbl_price_val.place(x=100, y=70)

        # Quantity Entry
        lbl_qty = ctk.CTkLabel(dlg, text="Quantity to Add:", font=(self.font, 11, "bold"), text_color=TEXT_DIM_COLOR)
        lbl_qty.place(x=30, y=265)

        ent_qty = ctk.CTkEntry(
            dlg,
            width=400,
            height=36,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            text_color=TEXT_COLOR,
        )
        ent_qty.insert(0, "1")
        ent_qty.place(x=30, y=288)

        # Initial preview trigger
        on_product_change(products[0])

        def add_to_cart():
            p_name = self.shop_item_var.get()
            qty_str = ent_qty.get().strip()

            try:
                qty_add = int(qty_str)
                if qty_add <= 0:
                    error("Quantity must be greater than 0.")
                    return
            except ValueError:
                error("Please enter a valid integer quantity.")
                return

            self.cur.execute("SELECT product_id, description, price, quantity FROM products WHERE product_name=?", (p_name,))
            p_id, desc, price, avail_qty = self.cur.fetchone()

            if qty_add > avail_qty:
                error(f"Cannot add {qty_add} units. Only {avail_qty} units available in stock.")
                return

            # Deduct temporary quantity from DB stock so stock updates dynamically
            self.cur.execute("UPDATE products SET quantity = quantity - ? WHERE product_id=?", (qty_add, p_id))
            self.con.commit()

            # Check if item already exists in Cart treeview -> Merge
            existing_item = None
            for item_id in self.tree.get_children():
                row_vals = self.tree.item(item_id, "values")
                if str(row_vals[0]) == str(p_id):
                    existing_item = item_id
                    break

            if existing_item:
                curr_vals = self.tree.item(existing_item, "values")
                curr_qty = int(curr_vals[4])
                new_qty = curr_qty + qty_add
                new_total = price * new_qty
                self.tree.item(
                    existing_item,
                    values=(p_id, p_name, desc, f"₹{price:,.2f}", new_qty, f"₹{new_total:,.2f}"),
                )
            else:
                total_amt = price * qty_add
                self.tree.insert(
                    "",
                    "end",
                    values=(p_id, p_name, desc, f"₹{price:,.2f}", qty_add, f"₹{total_amt:,.2f}"),
                )

            self._update_cart_total()
            dlg.destroy()

        btn_add = ctk.CTkButton(
            dlg,
            text="Add to Cart",
            font=(self.font, 13, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            width=400,
            height=40,
            command=add_to_cart,
        )
        btn_add.place(x=30, y=350)

    def remove_item_from_cart(self):
        """Removes selected item from cart and restores item quantity to inventory stock."""
        sel = self.tree.selection()
        if not sel:
            error("Please select an item in the cart to remove.")
            return

        for item in sel:
            vals = self.tree.item(item, "values")
            p_id = vals[0]
            qty = int(vals[4])

            # Restore quantity in SQLite database
            self.cur.execute("UPDATE products SET quantity = quantity + ? WHERE product_id=?", (qty, p_id))
            self.con.commit()
            self.tree.delete(item)

        self._update_cart_total()

    def _update_cart_total(self):
        """Calculates and updates running cart total amount."""
        total = 0.0
        for item in self.tree.get_children():
            val_str = self.tree.item(item, "values")[5]
            val_num = float(str(val_str).replace("₹", "").replace(",", ""))
            total += val_num

        self.cart_total_lbl.configure(text=f"₹{total:,.2f}")
        return total

    def buy(self):
        """Finalizes cart checkout and creates order records."""
        items = self.tree.get_children()
        if not items:
            error("Your shopping cart is empty.")
            return

        total_amount = self._update_cart_total()

        # Prompt payment status choice
        answer = messagebox.askyesno(
            "Checkout Payment",
            f"Total Order Amount: ₹{total_amount:,.2f}\n\nWould you like to Pay Now? (Click 'No' to mark as Pending)",
        )
        payment_status = "paid" if answer else "pending"

        # Generate unique order_id
        self.cur.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1;")
        row = self.cur.fetchone()
        order_id = (row[0] + 1) if row else 1001

        # Generate unique order_item_id
        self.cur.execute("SELECT order_item_id FROM order_items ORDER BY order_item_id DESC LIMIT 1;")
        row_item = self.cur.fetchone()
        order_item_id = (row_item[0] + 1) if row_item else 1

        total_items_count = 0
        for item in items:
            vals = self.tree.item(item, "values")
            p_id = vals[0]
            qty = int(vals[4])
            price = float(str(vals[3]).replace("₹", "").replace(",", ""))
            total_items_count += qty

            self.cur.execute(
                "INSERT INTO order_items (order_item_id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
                (order_item_id, order_id, p_id, qty, price),
            )
            order_item_id += 1

        self.cur.execute(
            "INSERT INTO orders (order_id, customer, date, total_items, total_amount, payment_status) VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, self.user[0], str(date.today()), total_items_count, total_amount, payment_status),
        )
        self.con.commit()

        messagebox.showinfo(
            "Order Placed",
            f"Order #{order_id} placed successfully!\nPayment Status: {payment_status.title()}",
        )

        for item in items:
            self.tree.delete(item)

        self._update_cart_total()

    # ── 6. HISTORY VIEW ────────────────────────────────────────────
    def history(self):
        """Displays user transaction order history with search and export."""
        self._clear_content("history")
        self.window.title("InvenTrack - Purchase History")
        self._create_header("Transaction History", "View your past purchases and order details")

        # Toolbar
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 15))

        self.hist_search_var = ctk.StringVar()
        self.hist_search_var.trace_add("write", lambda *args: self._filter_history())

        search_entry = ctk.CTkEntry(
            toolbar,
            width=300,
            height=36,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            text_color=TEXT_COLOR,
            placeholder_text="🔍  Search order ID, product name...",
            textvariable=self.hist_search_var,
        )
        search_entry.pack(side="left", padx=(0, 15))

        btn_csv = ctk.CTkButton(
            toolbar,
            text="📥 Export CSV",
            font=(self.font, 12, "bold"),
            fg_color=CARD_ALT_COLOR,
            hover_color="#2A2A48",
            height=36,
            command=lambda: self._export_csv(self.tree, "history"),
        )
        btn_csv.pack(side="right")

        # Table Container
        tbl_container = ctk.CTkFrame(self.frame, fg_color=CARD_COLOR, corner_radius=12)
        tbl_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        headings = ("Order ID", "Product Name", "Quantity", "Price", "Date", "Payment Status")
        widths = [140, 280, 120, 140, 180, 180]
        self.make_table(tbl_container, headings, widths)
        self._filter_history()

    def _filter_history(self):
        """Populates history table filtered by search string."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query_str = self.hist_search_var.get().strip().lower()

        sql = """
            SELECT o.order_id, p.product_name, oi.quantity, oi.price, o.date, o.payment_status
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.customer = ?
            ORDER BY o.order_id DESC;
        """
        self.cur.execute(sql, (self.user[0],))
        rows = self.cur.fetchall()

        for r in rows:
            o_id, p_name, qty, price, o_date, status = r
            if query_str:
                match = (
                    query_str in str(o_id).lower()
                    or query_str in str(p_name).lower()
                    or query_str in str(o_date).lower()
                    or query_str in str(status).lower()
                )
                if not match:
                    continue

            tag = "paid" if str(status).lower() == "paid" else "pending"
            formatted = (o_id, p_name, qty, f"₹{price:,.2f}", o_date, str(status).title())
            self.tree.insert("", "end", values=formatted, tags=(tag,))

    # ── TABLE GENERATOR HELPER ────────────────────────────────────
    def make_table(self, container, columns, widths, height=450):
        """Creates a styled Tkinter Treeview table inside container frame."""
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            rowheight=32,
            fieldbackground=CARD_COLOR,
            bordercolor=CARD_COLOR,
            borderwidth=0,
            font=(self.font, 11),
        )
        style.map(
            "Treeview",
            background=[("selected", PRIMARY_COLOR)],
            foreground=[("selected", "#FFFFFF")],
        )

        style.configure(
            "Treeview.Heading",
            background=CARD_ALT_COLOR,
            foreground=TEXT_DIM_COLOR,
            relief="flat",
            font=(self.font, 11, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", "#2A2A48")])

        # Scrollable container
        self.tree = ttk.Treeview(
            container, columns=columns, show="headings", selectmode="browse"
        )

        # Configure columns
        for idx, col in enumerate(columns):
            w = widths[idx] if idx < len(widths) else 150
            self.tree.column(col, width=w, anchor="w", stretch=True)
            self.tree.heading(col, text=col, anchor="w")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            container, orientation="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)

        # Color-coded tags
        self.tree.tag_configure("paid", foreground=SECONDARY_COLOR)
        self.tree.tag_configure("pending", foreground=WARNING_COLOR)
        self.tree.tag_configure("low_stock", foreground=DANGER_COLOR)
        self.tree.tag_configure("normal", foreground=TEXT_COLOR)
