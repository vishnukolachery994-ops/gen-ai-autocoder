import sqlite3
import os

def init_db():
    # Connect to the SQLite database
    # In a real project, we ensure the directory exists
    db_path = os.path.join(os.path.dirname(__file__), 'jewelry.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Initializing Flipkart-level schema...")

    # 1. Create Products Table (The Catalogue)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 10
        )
    ''')

    # 2. Create Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_amount REAL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Create Order Items Table (Relational logic)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()
    
    # 4. Seed Data (Flipkart Style - making the site look populated)
    seed_data(cursor)
    
    conn.commit()
    conn.close()
    print(f"Database initialized and seeded at: {db_path}")

def seed_data(cursor):
    """Inserts professional sample data so the UI looks real immediately."""
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Diamond Solitaire Ring', '18K White Gold classic ring', 1200.00, 'Rings', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e'),
            ('Gold Pendant Necklace', '24K Pure Gold heart necklace', 850.00, 'Necklaces', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f'),
            ('Pearl Earrings', 'Freshwater cultured pearls', 450.00, 'Earrings', 'https://images.unsplash.com/photo-1535633302723-997f858d4d6c'),
            ('Silver Luxury Watch', 'Stainless steel premium chronometer', 2100.00, 'Watches', 'https://images.unsplash.com/photo-1524592093825-84a625849745'),
            ('Emerald Tennis Bracelet', 'Deep green emeralds in silver', 950.00, 'Bracelets', 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338')
        ]
        cursor.executemany(
            "INSERT INTO products (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)",
            sample_products
        )
        print("Sample jewelry items added to catalogue.")

if __name__ == "__main__":
    init_db()