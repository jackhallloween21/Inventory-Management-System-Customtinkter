import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Treeview Table Example")
root.geometry("400x250")

# Create a Treeview widget
tree = ttk.Treeview(root, columns=("ID", "Name", "Age"), show="headings")

# Define column headings
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Age", text="Age")

# Define column width
tree.column("ID", width=50)
tree.column("Name", width=150)
tree.column("Age", width=50)

# Insert data into the table
tree.insert("", "end", values=(1, "Alice", 25))
tree.insert("", "end", values=(2, "Bob", 30))
tree.insert("", "end", values=(3, "Charlie", 22))

# Pack the treeview into the window
tree.pack(expand=True, fill="both")

# Run the application
root.mainloop()
