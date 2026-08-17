import sys
import os
import sqlite3
from login import Login
from menu import Menu

# Resolve a writable path for the database that persists across runs.
# When frozen by PyInstaller (--onefile) sys.executable is the .exe itself;
# when running from source __file__ is this script.
_BASE_DIR = os.path.dirname(
    sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
)
DB_PATH = os.path.join(_BASE_DIR, 'inventory.db')

class Main:
    """Represents the main application window for the inventory management system."""
    def __init__(self):
        self.run()

    def run(self):
        try:
            self.con = sqlite3.connect(DB_PATH)
            print('* Connected to SQLite database')
            self.cur = self.con.cursor()
            self.setup_database()
            while True:
                self.login = Login(self.con)
                self.login.window.mainloop()
                if not self.login.user:
                    break
                self.menu = Menu(self.con, self.login.user)
                self.menu.window.mainloop()
                if not self.menu.logout:
                    break
            self.con.close()
        except sqlite3.Error as e:
            print(f"Error: {e}")

    def setup_database(self):
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL, account_type TEXT NOT NULL);")
            self.cur.execute("CREATE TABLE IF NOT EXISTS products (product_id TEXT PRIMARY KEY, product_name TEXT NOT NULL, description TEXT NOT NULL, price REAL NOT NULL, quantity INTEGER NOT NULL);")
            self.cur.execute("CREATE TABLE IF NOT EXISTS orders (order_id INTEGER PRIMARY KEY, customer TEXT, date TEXT, total_items INTEGER, total_amount REAL, payment_status TEXT);")
            self.cur.execute("CREATE TABLE IF NOT EXISTS order_items (order_item_id INTEGER PRIMARY KEY, order_id INTEGER, product_id TEXT, quantity INTEGER NOT NULL, price REAL NOT NULL);")
        except sqlite3.Error as e:
            print(f"Error setting up database: {e}")

if __name__ == "__main__":
    m = Main()
