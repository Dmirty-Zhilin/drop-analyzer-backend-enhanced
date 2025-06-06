#!/bin/bash

# Drop Analyzer Backend Enhanced - Setup Script
# This script sets up the development environment

echo "🚀 Setting up Drop Analyzer Backend Enhanced..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your actual configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual configuration"
echo "2. Start the development server: python src/main.py"
echo "3. Access the API at: http://localhost:5000"
echo "4. View API documentation at: http://localhost:5000/docs"
echo ""
echo "🔑 Default admin credentials:"
echo "   Email: admin@dropanalyzer.com"
echo "   Password: admin123"
echo "   ⚠️  Change password after first login!"

