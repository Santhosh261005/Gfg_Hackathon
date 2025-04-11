import sqlite3
from datetime import datetime, timedelta

class ProductAgent:
    def __init__(self):
        self.conn = sqlite3.connect('smart_shopping.db')
    
    def update_product_scores(self):
        """Update product scores based on recent activity"""
        cursor = self.conn.cursor()
        
        # Calculate popularity score (based on views and purchases in last 7 days)
        cursor.execute('''
        SELECT product_id, 
               SUM(CASE WHEN action_type = 'view' THEN 1 ELSE 0 END) as views,
               SUM(CASE WHEN action_type = 'purchase' THEN 1 ELSE 0 END) as purchases
        FROM customer_behavior
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY product_id
        ''')
        
        activity_data = cursor.fetchall()
        
        for product_id, views, purchases in activity_data:
            popularity_score = min(1.0, (views * 0.1 + purchases * 0.5) / 10)
            
            # Simple trend calculation (compare to previous period)
            cursor.execute('''
            SELECT COUNT(*) 
            FROM customer_behavior 
            WHERE product_id = ? 
            AND timestamp BETWEEN datetime('now', '-14 days') AND datetime('now', '-7 days')
            ''', (product_id,))
            prev_period_activity = cursor.fetchone()[0]
            
            current_period_activity = views + purchases
            trend_score = 0.5  # Default
            if prev_period_activity > 0:
                trend_change = (current_period_activity - prev_period_activity) / prev_period_activity
                trend_score = min(1.0, max(0.0, 0.5 + trend_change * 0.5))
            
            cursor.execute('''
            UPDATE product_scores
            SET popularity_score = ?,
                trend_score = ?,
                last_updated = datetime('now')
            WHERE product_id = ?
            ''', (popularity_score, trend_score, product_id))
        
        self.conn.commit()
    
    def get_product_info(self, product_id):
        """Get product details with scores"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.*, ps.popularity_score, ps.trend_score, ps.relevance_score
        FROM products p
        JOIN product_scores ps ON p.product_id = ps.product_id
        WHERE p.product_id = ?
        ''', (product_id,))
        return cursor.fetchone()
    
    def get_related_products(self, product_id, limit=3):
        """Get products in the same category"""
        cursor = self.conn.cursor()
        
        # First get the category of the current product
        cursor.execute('SELECT category FROM products WHERE product_id = ?', (product_id,))
        category = cursor.fetchone()[0]
        
        # Then get other products in the same category, ordered by composite score
        cursor.execute('''
        SELECT p.*, ps.popularity_score, ps.trend_score, ps.relevance_score
        FROM products p
        JOIN product_scores ps ON p.product_id = ps.product_id
        WHERE p.category = ? AND p.product_id != ?
        ORDER BY (ps.popularity_score + ps.trend_score + ps.relevance_score) DESC
        LIMIT ?
        ''', (category, product_id, limit))
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()