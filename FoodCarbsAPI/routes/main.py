from flask import Blueprint, jsonify, request, redirect, url_for, render_template, Response, current_app
from FoodCarbsAPI.models import db, Food
from FoodCarbsAPI import cache  # Import the cache object
import json

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

@main.route('/callback')
def callback():
    alerts = request.args.get('alerts')
    if alerts:
        alerts = json.loads(alerts)  # Parse the JSON string into a Python dictionary
    return render_template('callback.html', alerts=alerts)

# Route for foods with optional start and end parameters
@main.route('/foods', methods=['GET'])
def get_foods():
    try:
        start = request.args.get('start', 0, type=int)
        end = request.args.get('end', None, type=int)

        if start < 0:
            return jsonify({"error": "Invalid 'start' parameter. It must be a non-negative integer."}), 400

        if end is not None and end <= start:
            return jsonify({"error": "Invalid 'end' parameter. It must be greater than 'start'."}), 400

        query = Food.query
        if end is not None:
            foods = query.offset(start).limit(end - start).all()
        else:
            foods = query.offset(start).all()

        return jsonify([food.to_dict() for food in foods])
    except ValueError:
        return jsonify({"error": "Invalid 'start' or 'end' parameter. They must be integers."}), 400


@main.route('/foods/<int:id>', methods=['GET'])
def get_food(id):
    food = Food.query.get_or_404(id)
    return jsonify(food.to_dict())

@main.route('/foods', methods=['POST'])
def create_food():
    data = request.get_json()
    new_food = Food(
        product_name=data['product_name'],
        carbohydrates_100g=data.get('carbohydrates_100g'),
        serving_size=data.get('serving_size'),
        serving_quantity=data.get('serving_quantity'),
        countries=data.get('countries'),
        image_nutrition_url=data.get('image_nutrition_url')
    )
    db.session.add(new_food)
    db.session.commit()
    return jsonify(new_food.to_dict()), 201

@main.route('/foods/<int:id>', methods=['PUT'])
def update_food(id):
    food = Food.query.get_or_404(id)
    data = request.get_json()
    food.product_name = data.get('product_name', food.product_name)
    food.carbohydrates_100g = data.get('carbohydrates_100g', food.carbohydrates_100g)
    food.serving_size = data.get('serving_size', food.serving_size)
    food.serving_quantity = data.get('serving_quantity', food.serving_quantity)
    food.countries = data.get('countries', food.countries)
    food.image_nutrition_url = data.get('image_nutrition_url', food.image_nutrition_url)
    db.session.commit()
    return jsonify(food.to_dict())

@main.route('/foods/<int:id>', methods=['DELETE'])
def delete_food(id):
    food = Food.query.get_or_404(id)
    db.session.delete(food)
    db.session.commit()
    return '', 204

# Live search route for product_name with pagination and sorting
@main.route('/foods/search', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def search_foods():
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'product_name')
        order = request.args.get('order', 'asc')

        if page < 1:
            return jsonify({"error": "Invalid 'page' parameter. It must be a positive integer."}), 400

        if per_page < 1:
            return jsonify({"error": "Invalid 'per_page' parameter. It must be a positive integer."}), 400

        if order not in ['asc', 'desc']:
            return jsonify({"error": "Invalid 'order' parameter. It must be 'asc' or 'desc'."}), 400

        sort_column = getattr(Food, sort_by, None)
        if sort_column is None:
            return jsonify({"error": f"Invalid 'sort_by' parameter. It must be a valid column name."}), 400

        if order == 'desc':
            sort_column = sort_column.desc()

        foods = Food.query.filter(Food.product_name.ilike(f'%{query}%')).order_by(sort_column).paginate(page, per_page, False)
        return jsonify({
            'total': foods.total,
            'pages': foods.pages,
            'current_page': foods.page,
            'per_page': foods.per_page,
            'items': [food.to_dict() for food in foods.items]
        })
    except ValueError as e:
        current_app.logger.error(f"ValueError in /foods/search: {e}")
        return jsonify({"error": "Invalid 'page' or 'per_page' parameter. They must be integers."}), 400
    except Exception as e:
        current_app.logger.error(f"Unhandled exception in /foods/search: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

# New route for paginated foods retrieval
@main.route('/foods/paginated', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_paginated_foods():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10000, type=int), 10000)  # Limit per_page to a maximum of 10000

        if page < 1:
            return jsonify({"error": "Invalid 'page' parameter. It must be a positive integer."}), 400

        if per_page < 1:
            return jsonify({"error": "Invalid 'per_page' parameter. It must be a positive integer."}), 400

        foods = Food.query.paginate(page, per_page, False)
        return jsonify({
            'total': foods.total,
            'pages': foods.pages,
            'current_page': foods.page,
            'per_page': foods.per_page,
            'items': [food.to_dict() for food in foods.items]
        })
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'per_page' parameter. They must be integers."}), 400

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

# Helper method to convert Food object to dictionary
def food_to_dict(self):
    return {
        'id': self.id,
        'product_name': self.product_name,
        'carbohydrates_100g': self.carbohydrates_100g,
        'serving_size': self.serving_size,
        'serving_quantity': self.serving_quantity,
        'countries': self.countries,
        'image_nutrition_url': self.image_nutrition_url
    }

Food.to_dict = food_to_dict
