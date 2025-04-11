from flask import Flask, render_template, request, redirect, url_for, session
from agents.customer_agent import CustomerAgent
from agents.product_agent import ProductAgent
from agents.recommender_agent import RecommenderAgent
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Sample customer for demo purposes
DEMO_CUSTOMER_ID = 1

@app.before_request
def before_request():
    # For demo purposes, we'll use a fixed customer ID
    session['customer_id'] = DEMO_CUSTOMER_ID
    
    # Update product scores periodically
    if 'last_score_update' not in session:
        update_product_scores()
        session['last_score_update'] = datetime.now().timestamp()
    elif datetime.now().timestamp() - session['last_score_update'] > 3600:  # 1 hour
        update_product_scores()
        session['last_score_update'] = datetime.now().timestamp()

def update_product_scores():
    """Helper function to update product scores"""
    product_agent = ProductAgent()
    product_agent.update_product_scores()
    product_agent.close()

@app.route('/')
def index():
    customer_id = session.get('customer_id', DEMO_CUSTOMER_ID)
    
    # Get customer info
    customer_agent = CustomerAgent(customer_id)
    customer = customer_agent.get_customer_profile()
    
    # Get recommendations
    recommender = RecommenderAgent(customer_id)
    recommendations = recommender.get_personalized_recommendations(limit=6)
    
    # Convert only the score columns to floats (indices 6,7,8)
    processed_recommendations = []
    for product in recommendations:
        product_list = list(product)
        # Only convert the score columns (6=popularity, 7=trend, 8=relevance)
        for i in [6, 7, 8]:
            try:
                product_list[i] = float(product_list[i])
            except (ValueError, TypeError):
                product_list[i] = 0.0  # Default value if conversion fails
        processed_recommendations.append(tuple(product_list))
    
    # Get recently viewed
    recent_behavior = customer_agent.get_behavior_history(limit=3)
    
    customer_agent.close()
    recommender.close()
    
    return render_template('index.html', 
                         customer=customer,
                         recommendations=processed_recommendations,
                         recent_behavior=recent_behavior)
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    customer_id = session.get('customer_id', DEMO_CUSTOMER_ID)
    
    # Track this view
    customer_agent = CustomerAgent(customer_id)
    customer_agent.track_behavior(product_id, 'view')
    
    # Update relevance scores for this customer
    recommender = RecommenderAgent(customer_id)
    recommender.update_relevance_scores(customer_id, product_id)
    
    # Get product info
    product_agent = ProductAgent()
    product = product_agent.get_product_info(product_id)
    related_products = product_agent.get_related_products(product_id)
    
    customer_agent.close()
    product_agent.close()
    recommender.close()
    
    return render_template('product.html', 
                         product=product,
                         related_products=related_products)

@app.route('/purchase/<int:product_id>')
def purchase(product_id):
    customer_id = session.get('customer_id', DEMO_CUSTOMER_ID)
    
    # Track this purchase
    customer_agent = CustomerAgent(customer_id)
    customer_agent.track_behavior(product_id, 'purchase')
    customer_agent.close()
    
    # Update product scores (purchases affect popularity)
    update_product_scores()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)