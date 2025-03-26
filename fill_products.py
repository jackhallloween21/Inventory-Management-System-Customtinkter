import sqlite3

def fill_products():
    # Connect to the SQLite database
    con = sqlite3.connect('inventory.db')
    cur = con.cursor()

    # Sample product data
    products = [
        ('P001', 'Laptop', 'High performance laptop', 999.99, 10),
        ('P002', 'Smartphone', 'Latest model smartphone', 699.99, 25),
        ('P003', 'Headphones', 'Noise-cancelling headphones', 199.99, 50),
        ('P004', 'Monitor', '4K Ultra HD monitor', 299.99, 15),
        ('P005', 'Keyboard', 'Mechanical keyboard', 89.99, 30),
        ('P006', 'Mouse', 'Wireless mouse', 49.99, 40),
        ('P007', 'Printer', 'All-in-one printer', 149.99, 20),
        ('P008', 'Tablet', '10-inch tablet', 399.99, 18),
        ('P009', 'Camera', 'Digital SLR camera', 799.99, 12),
        ('P010', 'Smartwatch', 'Waterproof smartwatch', 199.99, 22)
    ]

    # Insert product data into the products table
    try:
        cur.executemany("INSERT INTO products (product_id, product_name, description, price, quantity) VALUES (?, ?, ?, ?, ?)", products)
        con.commit()
        print("Products added successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting products: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    fill_products()