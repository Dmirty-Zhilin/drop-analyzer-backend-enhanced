"""
Simple database initialization script
"""
import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Database configuration
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drop_analyzer.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)

def init_database():
    """Initialize database and create tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if admin user already exists
            admin_user = User.query.filter_by(email='admin@dropanalyzer.com').first()
            
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username='admin',
                    email='admin@dropanalyzer.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True
                )
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Default admin user created:")
                print("   Email: admin@dropanalyzer.com")
                print("   Password: admin123")
                print("   ⚠️  Please change the password after first login!")
            else:
                print("ℹ️  Admin user already exists")
            
            print("\n🚀 Database initialization completed!")
            print("You can now start the application with: python src/main.py")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    init_database()

