!/bin/bash

# AI Attendance System Setup Script
# For Linux/macOS

echo "========================================"
echo "AI Attendance System Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "✓ Found: $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Error installing dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p dataset trainer attendance logs
echo "✓ Directories created"
echo ""

# Initialize database
echo "Initializing database..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from app import app, init_db

with app.app_context():
    init_db()
    print("✓ Database initialized with default admin")
EOF
echo ""

echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python app.py"
echo ""
echo "  3. Open in browser:"
echo "     http://localhost:5000"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠️  Change the default password in production!"
echo "========================================"