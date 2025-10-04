"""Flask application setup."""
from flask import Flask


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Simple config
    from .config import MAX_CONTENT_LENGTH
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Register routes
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

