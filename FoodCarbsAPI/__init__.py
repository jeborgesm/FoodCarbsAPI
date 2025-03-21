import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_cors import CORS
from sqlalchemy import MetaData
from flask.signals import got_request_exception

# Define naming conventions for foreign keys
convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}

# Initialize extensions
db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app(config_class='FoodCarbsAPI.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app)
    CORS(app)

    # Import and register blueprints here
    from FoodCarbsAPI.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

    # Log request data
    @app.before_request
    def log_request_info():
        app.logger.info('Request: %s %s %s %s', request.method, request.url, request.remote_addr, dict(request.headers))

    # Optionally log response data
    @app.after_request
    def log_response_info(response):
        app.logger.info('Response: %s %s', response.status, response.get_data(as_text=True))
        return response

    # Log errors
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Server Error: %s', (error))
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', (e))
        return jsonify({"error": "Unhandled exception occurred"}), 500

    # Log unhandled exceptions
    def log_exception(sender, exception, **extra):
        sender.logger.error('Got exception during processing: %s', exception)

    got_request_exception.connect(log_exception, app)

    return app

