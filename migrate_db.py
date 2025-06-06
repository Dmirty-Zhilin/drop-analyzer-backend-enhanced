"""
Database migration script for existing installations
"""
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app, db
from models.user import User
from models.analysis import AnalysisTask, DomainResult, Report

def migrate_database():
    """Migrate database schema to latest version"""
    with app.app_context():
        try:
            # Create any missing tables
            db.create_all()
            print("✅ Database schema updated")
            
            # Add any missing columns or constraints
            # This is where you would add migration logic for schema changes
            
            # Example: Add new columns if they don't exist
            # try:
            #     db.engine.execute('ALTER TABLE users ADD COLUMN new_field VARCHAR(255)')
            #     print("✅ Added new_field to users table")
            # except Exception:
            #     print("ℹ️  new_field already exists in users table")
            
            print("✅ Database migration completed successfully")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False
    
    return True

def backup_database():
    """Create a backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    # This would implement actual backup logic based on your database type
    print(f"📦 Database backup would be created as: {backup_file}")
    print("ℹ️  Implement actual backup logic based on your database system")

if __name__ == '__main__':
    print("🔄 Starting database migration...")
    
    # Optionally create backup first
    backup_database()
    
    # Run migration
    if migrate_database():
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)

