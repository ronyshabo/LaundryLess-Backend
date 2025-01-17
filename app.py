import os
import sys
from flask import Flask
from firebase import db
from main import main_bp
from config import Config
from flasgger import Swagger
from API.user_routes import user_bp
from API.order_routes import order_bp
from API.admin_routes import admin_bp
from API.driver_routes import driver_bp
from API.garmnet_routes import garment_bp


app = Flask(__name__)
app.config.from_object(Config)

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Custom Swagger Configuration
swagger_config = {
    "headers": [],
    "title": "Laundryless API",
    "version": "1.0",
    "description": "API documentation for the Laundryless platform.",
    "termsOfService": "",
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # include all routes
            "model_filter": lambda tag: True  # include all models
        }
    ]
}

# Initialize Swagger for API documentation
swagger = Swagger(app, config=swagger_config)

# Register Blueprints for route management
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(driver_bp, url_prefix='/api')
app.register_blueprint(garment_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)