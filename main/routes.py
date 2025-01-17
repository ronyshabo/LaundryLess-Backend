from flask import render_template, current_app, Blueprint, redirect, url_for
from . import main_bp
from .main import google_callback
from API import user_bp

@main_bp.route('/')
def home():
    routes = []
    for rule in current_app.url_map.iter_rules():
        # Skip static routes
        if "GET" in rule.methods and not rule.rule.startswith('/static'):
            routes.append({
                'endpoint': rule.endpoint,
                'rule': rule.rule,
                'methods': ', '.join(rule.methods)
            })
    return render_template('index.html', routes=routes)

