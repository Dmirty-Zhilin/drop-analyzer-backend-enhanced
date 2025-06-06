"""
Enhanced Drop Analyzer Backend
Main application entry point with database, authentication, and AI integration
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
from functools import wraps

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and routes
from src.models.user import db, User
from src.models.analysis import AnalysisTask, DomainResult, Report
from src.routes.user import user_bp
from src.routes.analysis import analysis_bp
from src.routes.admin import admin_bp
from src.routes.reports import reports_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to MySQL configuration for Coolify
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USERNAME', 'root')}:"
        f"{os.getenv('DB_PASSWORD', 'password')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 'drop_analyzer')}"
    )
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, origins=[
    "https://qo8k8k0c48sk080ccwgswocg.alettidesign.ru",
    "http://localhost:3000",  # для разработки
    "http://localhost:5173",  # для Vite dev server
    "http://localhost:5000"   # для локального тестирования
])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/v1/auth')
app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')
app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')

# JWT token blacklist (in production, use Redis or database)
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in blacklisted_tokens

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify(message='Token has been revoked'), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify(message='Token has expired'), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify(message='Invalid token'), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify(message='Authorization token is required'), 401

# Role-based access control decorator
def require_role(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role != role:
                return jsonify(message='Insufficient permissions'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Health check endpoint
@app.route('/api/v1/health')
def health_check():
    try:
        # Проверка подключения к базе данных
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': db_status,
        'environment': os.getenv('FLASK_ENV', 'development')
    })

# API documentation endpoint
@app.route('/docs')
def api_docs():
    return jsonify({
        'title': 'Drop Analyzer API',
        'version': '1.0.0',
        'description': 'Enhanced Drop Analyzer with AI integration and user management',
        'endpoints': {
            'authentication': {
                'POST /api/v1/auth/register': 'Register new user',
                'POST /api/v1/auth/login': 'Login user',
                'POST /api/v1/auth/logout': 'Logout user',
                'GET /api/v1/auth/profile': 'Get user profile'
            },
            'analysis': {
                'POST /api/v1/analysis/analyze': 'Start domain analysis',
                'GET /api/v1/analysis/tasks/{task_id}': 'Get task status',
                'GET /api/v1/analysis/results/{task_id}': 'Get analysis results',
                'POST /api/v1/analysis/save': 'Save selected results',
                'GET /api/v1/analysis/export/{task_id}': 'Export results'
            },
            'reports': {
                'GET /api/v1/reports/': 'List user reports',
                'GET /api/v1/reports/{report_id}': 'Get specific report',
                'DELETE /api/v1/reports/{report_id}': 'Delete report'
            },
            'admin': {
                'GET /api/v1/admin/users': 'List all users (admin only)',
                'PUT /api/v1/admin/users/{user_id}/role': 'Update user role (admin only)',
                'GET /api/v1/admin/stats': 'Get system statistics (admin only)'
            }
        }
    })

# Static file serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Create database tables
with app.app_context():
    try:
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(email='admin@dropanalyzer.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@dropanalyzer.com',
                role='admin'
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin@dropanalyzer.com / admin123")
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == '__main__':
    # Production-ready settings
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0', 
        port=int(os.getenv('PORT', 5000)), 
        debug=debug_mode,
        threaded=True
    )

