import sqlite3
from datetime import datetime

class CustomerAgent:
    def __init__(self, customer_id=None):
        self.customer_id = customer_id
        self.conn = sqlite3.connect('smart_shopping.db')
    
    def track_behavior(self, product_id, action_type):
        """Track customer behavior (view, purchase, wishlist)"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO customer_behavior (customer_id, product_id, action_type)
        VALUES (?, ?, ?)
        ''', (self.customer_id, product_id, action_type))
        self.conn.commit()
    
    def get_customer_profile(self):
        """Retrieve customer demographic information"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE customer_id = ?', (self.customer_id,))
        return cursor.fetchone()
    
    def get_behavior_history(self, limit=5):
        """Get recent customer behavior"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.name, p.category, cb.action_type, cb.timestamp 
        FROM customer_behavior cb
        JOIN products p ON cb.product_id = p.product_id
        WHERE cb.customer_id = ?
        ORDER BY cb.timestamp DESC
        LIMIT ?
        ''', (self.customer_id, limit))
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()