"""Flask application setup."""
import os
from flask import Flask


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configure session for OAuth (serverless-compatible with cookie-based sessions)
    # IMPORTANT: Set SECRET_KEY environment variable in Vercel for production
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Use default cookie-based sessions (no filesystem needed)
    
    # Simple config
    from .config import MAX_CONTENT_LENGTH
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Register routes
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

