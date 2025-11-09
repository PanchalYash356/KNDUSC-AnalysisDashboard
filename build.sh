#!/usr/bin/env bash
set -o errexit

echo "=== Starting Build Process ==="

# Print environment info
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "Current directory: $(pwd)"
ls -la

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Debug: Show installed packages
echo "Installed packages:"
pip list

# Create necessary directories
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "Running migrations..."
python manage.py migrate

echo "=== Build Completed Successfully ==="