"""
Identity Spoofing Detection System - Main Backend Application
Detects fake credentials, impersonation, and credential sharing in gated communities
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///identity_spoofing.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize database with app
from database.models import db
db.init_app(app)

# Avoid importing heavy ML services at startup to keep boot clean and fast

# Register blueprints
from routes.auth_routes import auth_bp
from routes.access_routes import access_bp
from routes.dashboard_routes import dashboard_bp
from routes.demo_routes import demo_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(access_bp, url_prefix='/api/access')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(demo_bp, url_prefix='/api/demo')

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization warning: {e}")

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'message': 'Identity Spoofing Detection System API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'access': '/api/access',
            'dashboard': '/api/dashboard',
            'demo': '/api/demo'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Identity Spoofing Detection System'
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Identity Spoofing Detection System Starting...")
    print("📍 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
