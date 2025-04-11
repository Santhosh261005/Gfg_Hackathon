import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('smart_shopping.db')
    cursor = conn.cursor()
    
    # Create tables (removed all # comments from SQL)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        age INTEGER,
        gender TEXT,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_behavior (
        behavior_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        action_type TEXT,  -- 'view', 'purchase', 'wishlist'
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_scores (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        popularity_score REAL DEFAULT 0,
        trend_score REAL DEFAULT 0,
        relevance_score REAL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )''')
    
    conn.commit()
    conn.close()

def seed_sample_data():
    conn = sqlite3.connect('smart_shopping.db')
    cursor = conn.cursor()
    
    # Insert sample customers
    customers = [
        ('John Doe', 'john@example.com', 32, 'male', 'New York'),
        ('Jane Smith', 'jane@example.com', 28, 'female', 'Los Angeles'),
        ('Mike Johnson', 'mike@example.com', 45, 'male', 'Chicago')
    ]
    cursor.executemany('INSERT INTO customers (name, email, age, gender, location) VALUES (?, ?, ?, ?, ?)', customers)
    
    # Insert sample products
    products = [
        ('iPhone 15 Pro', 'Smartphones', 999.99, 'Latest Apple smartphone with A17 Pro chip', '/static/images/iphone.jpg'),
        ('Samsung Galaxy S23', 'Smartphones', 799.99, 'Premium Android smartphone with Snapdragon 8 Gen 2', '/static/images/galaxy.jpg'),
        ('Google Pixel 8', 'Smartphones', 699.99, 'Google\'s flagship with Tensor G3 chip', '/static/images/pixel.jpg'),
        ('Apple Watch Series 9', 'Wearables', 399.99, 'Latest Apple smartwatch with S9 chip', '/static/images/apple_watch.jpg'),
        ('Samsung Galaxy Watch 6', 'Wearables', 349.99, 'Premium Android smartwatch', '/static/images/galaxy_watch.jpg'),
        ('AirPods Pro (2nd Gen)', 'Audio', 249.99, 'Premium wireless earbuds with ANC', '/static/images/airpods.jpg'),
        ('Sony WH-1000XM5', 'Audio', 399.99, 'Industry-leading noise cancelling headphones', '/static/images/sony_headphones.jpg'),
        ('MacBook Pro 14" M3', 'Laptops', 1599.99, 'Powerful Apple laptop with M3 chip', '/static/images/macbook.jpg'),
        ('Dell XPS 15', 'Laptops', 1499.99, 'Premium Windows laptop', '/static/images/dell_xps.jpg'),
        ('iPad Pro 12.9"', 'Tablets', 1099.99, 'Professional tablet with M2 chip', '/static/images/ipad.jpg')
    ]
    cursor.executemany('INSERT INTO products (name, category, price, description, image_url) VALUES (?, ?, ?, ?, ?)', products)
    
    # Insert initial product scores as floats
    cursor.execute('SELECT product_id FROM products')
    for row in cursor.fetchall():
        cursor.execute('''
        INSERT INTO product_scores (product_id, popularity_score, trend_score, relevance_score)
        VALUES (?, ?, ?, ?)''', (row[0], 0.5, 0.5, 0.5))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Clean up any existing database
    try:
        import os
        os.remove('smart_shopping.db')
    except FileNotFoundError:
        pass
    
    # Initialize fresh database
    init_db()
    seed_sample_data()
    print("Database successfully initialized and seeded!")