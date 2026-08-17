import tkinter
from tkinter import messagebox
import customtkinter as ctk

from utils import error

# Design System Palette Tokens
BG_COLOR = "#08080F"
SIDEBAR_COLOR = "#0C0C1A"
CARD_COLOR = "#131325"
CARD_ALT_COLOR = "#1C1C35"
PRIMARY_COLOR = "#6C63FF"
PRIMARY_HOVER = "#5850DD"
SECONDARY_COLOR = "#00D4AA"
DANGER_COLOR = "#FF6B6B"
TEXT_COLOR = "#E8E8F0"
TEXT_DIM_COLOR = "#7A7A9A"
FONT_FAMILY = "Segoe UI"


class Login:
    """Represents a modernized login and registration window for user authentication."""

    def __init__(self, con):
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("dark")
        self.window = ctk.CTk()
        self.window.title("InvenTrack - Sign In")
        self.window.geometry("880x560")
        self.window.configure(fg_color=BG_COLOR)
        self.window.resizable(False, False)

        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = max(0, (screen_width // 2) - (880 // 2))
        y = max(0, (screen_height // 2) - (560 // 2))
        self.window.geometry(f"880x560+{x}+{y}")

        self.con = con
        self.cur = con.cursor()
        self.user = None

        self._setup_layout()
        self.login_window()

    def _setup_layout(self):
        """Creates the two-column split panel (Branding Left + Form Right)."""
        # Left branding panel (440px)
        left_panel = ctk.CTkFrame(
            self.window, width=440, height=560, corner_radius=0, fg_color=SIDEBAR_COLOR
        )
        left_panel.place(x=0, y=0)
        left_panel.pack_propagate(False)

        # Top accent bar
        top_accent = ctk.CTkFrame(
            left_panel, width=440, height=5, corner_radius=0, fg_color=PRIMARY_COLOR
        )
        top_accent.place(x=0, y=0)

        # Bottom accent bar
        bottom_accent = ctk.CTkFrame(
            left_panel, width=440, height=5, corner_radius=0, fg_color=SECONDARY_COLOR
        )
        bottom_accent.place(x=0, y=555)

        # Branding content container
        brand_box = ctk.CTkFrame(left_panel, fg_color="transparent")
        brand_box.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        # Icon and title
        icon_label = ctk.CTkLabel(
            brand_box, text="📦", font=(FONT_FAMILY, 64)
        )
        icon_label.pack(pady=(0, 5))

        title_label = ctk.CTkLabel(
            brand_box, text="InvenTrack", font=(FONT_FAMILY, 32, "bold"), text_color=TEXT_COLOR
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            brand_box,
            text="Smart Inventory & Sales Management",
            font=(FONT_FAMILY, 14),
            text_color=TEXT_DIM_COLOR,
        )
        subtitle_label.pack(pady=(2, 25))

        # Bullet points
        features = [
            "Real-time Stock Tracking",
            "Order & Invoice Management",
            "Analytics & Sales Insights",
            "Role-Based Access Control",
        ]
        for item in features:
            f_frame = ctk.CTkFrame(brand_box, fg_color="transparent")
            f_frame.pack(anchor="w", pady=4, fill="x")

            bullet = ctk.CTkLabel(
                f_frame, text="✓", font=(FONT_FAMILY, 14, "bold"), text_color=SECONDARY_COLOR
            )
            bullet.pack(side="left", padx=(0, 8))

            text = ctk.CTkLabel(
                f_frame, text=item, font=(FONT_FAMILY, 13), text_color=TEXT_COLOR
            )
            text.pack(side="left")

        # Right form container panel (440px)
        self.right_panel = ctk.CTkFrame(
            self.window, width=440, height=560, corner_radius=0, fg_color=BG_COLOR
        )
        self.right_panel.place(x=440, y=0)
        self.right_panel.pack_propagate(False)

        # Inner form wrapper centered in right panel
        self.form_box = ctk.CTkFrame(
            self.right_panel, width=340, height=440, corner_radius=16, fg_color=CARD_COLOR
        )
        self.form_box.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    def login_window(self, event=None):
        """Displays the Login form inside the right panel."""
        self.window.title("InvenTrack - Sign In")
        self.window.bind("<Return>", self.login)

        # Clear form_box children
        for child in self.form_box.winfo_children():
            child.destroy()

        header_label = ctk.CTkLabel(
            self.form_box, text="Welcome Back", font=(FONT_FAMILY, 24, "bold"), text_color=TEXT_COLOR
        )
        header_label.place(x=35, y=35)

        sub_label = ctk.CTkLabel(
            self.form_box, text="Sign in to continue to InvenTrack", font=(FONT_FAMILY, 12), text_color=TEXT_DIM_COLOR
        )
        sub_label.place(x=35, y=68)

        # Username label & entry
        lbl_uname = ctk.CTkLabel(
            self.form_box, text="USERNAME", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM_COLOR
        )
        lbl_uname.place(x=35, y=110)

        self.username = ctk.CTkEntry(
            self.form_box,
            width=270,
            height=40,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            border_width=1,
            text_color=TEXT_COLOR,
            placeholder_text="Enter username",
        )
        self.username.place(x=35, y=132)

        # Password label & entry
        lbl_pwd = ctk.CTkLabel(
            self.form_box, text="PASSWORD", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM_COLOR
        )
        lbl_pwd.place(x=35, y=190)

        self.password = ctk.CTkEntry(
            self.form_box,
            width=270,
            height=40,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            border_width=1,
            text_color=TEXT_COLOR,
            placeholder_text="Enter password",
            show="•",
        )
        self.password.place(x=35, y=212)

        # Login button
        btn_login = ctk.CTkButton(
            self.form_box,
            width=270,
            height=42,
            corner_radius=8,
            text="Sign In",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.login,
        )
        btn_login.place(x=35, y=285)

        # Toggle to Register link
        self.label_link = ctk.CTkLabel(
            self.form_box,
            text="Don't have an account? Register",
            font=(FONT_FAMILY, 12),
            text_color=PRIMARY_COLOR,
            cursor="hand2",
        )
        self.label_link.place(x=65, y=345)
        self.label_link.bind("<Button-1>", self.register_window)

    def register_window(self, event=None):
        """Displays the Register form inside the right panel."""
        self.window.title("InvenTrack - Create Account")
        self.window.bind("<Return>", self.register)

        # Clear form_box children
        for child in self.form_box.winfo_children():
            child.destroy()

        header_label = ctk.CTkLabel(
            self.form_box, text="Create Account", font=(FONT_FAMILY, 24, "bold"), text_color=TEXT_COLOR
        )
        header_label.place(x=35, y=35)

        sub_label = ctk.CTkLabel(
            self.form_box, text="Register a new user account", font=(FONT_FAMILY, 12), text_color=TEXT_DIM_COLOR
        )
        sub_label.place(x=35, y=68)

        # Username label & entry
        lbl_uname = ctk.CTkLabel(
            self.form_box, text="USERNAME", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM_COLOR
        )
        lbl_uname.place(x=35, y=110)

        self.username = ctk.CTkEntry(
            self.form_box,
            width=270,
            height=40,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            border_width=1,
            text_color=TEXT_COLOR,
            placeholder_text="Choose username",
        )
        self.username.place(x=35, y=132)

        # Password label & entry
        lbl_pwd = ctk.CTkLabel(
            self.form_box, text="PASSWORD", font=(FONT_FAMILY, 11, "bold"), text_color=TEXT_DIM_COLOR
        )
        lbl_pwd.place(x=35, y=190)

        self.password = ctk.CTkEntry(
            self.form_box,
            width=270,
            height=40,
            corner_radius=8,
            fg_color=CARD_ALT_COLOR,
            border_color="#2A2A45",
            border_width=1,
            text_color=TEXT_COLOR,
            placeholder_text="Choose password",
            show="•",
        )
        self.password.place(x=35, y=212)

        # Register button
        btn_reg = ctk.CTkButton(
            self.form_box,
            width=270,
            height=42,
            corner_radius=8,
            text="Create Account",
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.register,
        )
        btn_reg.place(x=35, y=285)

        # Toggle to Login link
        self.label_link = ctk.CTkLabel(
            self.form_box,
            text="Already have an account? Sign in",
            font=(FONT_FAMILY, 12),
            text_color=PRIMARY_COLOR,
            cursor="hand2",
        )
        self.label_link.place(x=60, y=345)
        self.label_link.bind("<Button-1>", self.login_window)

    def login(self, event=None):
        """Authenticate the user by checking credentials in SQLite."""
        uname = self.username.get().strip()
        pwd = self.password.get().strip()
        
        # Ensure default Admin account exists
        self.cur.execute(
            "INSERT OR IGNORE INTO users (username, password, account_type) VALUES ('Admin', 'Admin', 'ADMIN');"
        )
        self.cur.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        f = self.cur.fetchall()
        if f:
            print(f"└─Logged in as {uname}")
            self.user = f[0]
            self.window.quit()
        else:
            error("Invalid Username or Password")

    def register(self, event=None):
        """Create a new user account in SQLite."""
        uname = self.username.get().strip()
        pwd = self.password.get().strip()

        if len(uname) == 0 or len(pwd) == 0:
            error("Username and Password cannot be empty")
            return
        if len(uname) > 20 or len(pwd) > 20:
            error("Username and Password must be 20 characters or less")
            return

        self.cur.execute("SELECT * FROM users WHERE username=?", (uname,))
        if self.cur.fetchall():
            error("Username already exists")
            return

        self.cur.execute(
            "INSERT INTO users (username, password, account_type) VALUES (?, ?, 'USER')", (uname, pwd)
        )
        self.con.commit()
        messagebox.showinfo("Account Created", "Your account has been successfully created!")
        self.user = (uname, pwd, "USER")
        self.window.quit()