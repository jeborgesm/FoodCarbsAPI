from flask import Blueprint, jsonify
from FoodCarbsAPI.models import Food

main = Blueprint('main', __name__)

@main.route('/')
def hello():
    return "Hello from the Blueprint!"

# Add new routes here
@main.route('/about')
def about():
    return "About Page"

@main.route('/contact')
def contact():
    return "Contact Page"

# Custom error handlers
@main.app_errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@main.app_errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Test route to verify database connection and data
@main.route('/test-db')
def test_db():
    foods = Food.query.all()
    return jsonify([food.product_name for food in foods])


