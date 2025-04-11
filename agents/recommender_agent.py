import sqlite3
from datetime import datetime, timedelta

class RecommenderAgent:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.conn = sqlite3.connect('smart_shopping.db')
    
    def get_personalized_recommendations(self, limit=5):
        """Generate personalized recommendations based on customer behavior"""
        cursor = self.conn.cursor()
        
        # Get customer's most viewed categories
        cursor.execute('''
        SELECT p.category, COUNT(*) as view_count
        FROM customer_behavior cb
        JOIN products p ON cb.product_id = p.product_id
        WHERE cb.customer_id = ? AND cb.action_type = 'view'
        GROUP BY p.category
        ORDER BY view_count DESC
        LIMIT 1
        ''', (self.customer_id,))
        
        favorite_category = None
        category_result = cursor.fetchone()
        if category_result:
            favorite_category = category_result[0]  # Access tuple by index (0=category, 1=view_count)
        
        # Generate recommendations
        if favorite_category:
            cursor.execute('''
            SELECT 
                p.product_id,
                p.name,
                p.category,
                p.price,
                p.description,
                p.image_url,
                ps.popularity_score,
                ps.trend_score,
                ps.relevance_score
            FROM products p
            JOIN product_scores ps ON p.product_id = ps.product_id
            WHERE p.category = ?
            ORDER BY (ps.popularity_score + ps.trend_score) DESC
            LIMIT ?
            ''', (favorite_category, limit))
            recommendations = cursor.fetchall()
            
            if len(recommendations) >= limit:
                return recommendations
        
        # Fallback: recommend trending products across all categories
        cursor.execute('''
        SELECT 
            p.product_id,
            p.name,
            p.category,
            p.price,
            p.description,
            p.image_url,
            ps.popularity_score,
            ps.trend_score,
            ps.relevance_score
        FROM products p
        JOIN product_scores ps ON p.product_id = ps.product_id
        ORDER BY (ps.popularity_score + ps.trend_score) DESC
        LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def update_relevance_scores(self, customer_id, viewed_product_id):
        """Update relevance scores based on this customer's interaction"""
        cursor = self.conn.cursor()
        
        # Get the category of the viewed product
        cursor.execute('SELECT category FROM products WHERE product_id = ?', (viewed_product_id,))
        category = cursor.fetchone()[0]
        
        # Increase relevance for products in the same category
        cursor.execute('''
        UPDATE product_scores
        SET relevance_score = MIN(1.0, relevance_score + 0.1)
        WHERE product_id IN (
            SELECT product_id FROM products WHERE category = ?
        )
        ''', (category,))
        
        self.conn.commit()
    
    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()