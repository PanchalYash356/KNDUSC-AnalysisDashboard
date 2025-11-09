#!/usr/bin/env bash
set -o errexit

echo "=== Starting Django Dashboard Build ==="

# Upgrade pip
echo "1. Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "2. Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "3. Creating directories..."
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "4. Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "5. Applying database migrations..."
python manage.py migrate

echo "=== Build Completed Successfully ==="