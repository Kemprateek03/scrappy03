#!/bin/bash
# scrappy Clone Setup Script

echo "🚀 Setting up scrappy Clone..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install django pillow --quiet

# Run migrations
echo "🗄️  Creating database..."
python manage.py makemigrations core
python manage.py migrate

# Create superuser prompt
echo ""
echo "👤 Create an admin account (for Django admin panel):"
python manage.py createsuperuser

echo ""
echo "✅ Setup complete!"
echo ""
echo "▶️  Run the server with:"
echo "    python manage.py runserver"
echo ""
echo "🌐 Then open: http://localhost:8000"
echo "🔧 Admin panel: http://localhost:8000/admin"
