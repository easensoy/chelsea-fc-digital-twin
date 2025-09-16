# Chelsea FC Digital Twin - Setup Guide

## 🚀 Quick Start Guide

This guide will help you set up the Chelsea FC Digital Twin platform with the beautiful football field visualizations.

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+
- Redis 6+
- Git

### 1. Clone the Repository

```bash
git clone <repository_url>
cd chelsea_fc_digital_twin
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database Configuration
DB_NAME=chelsea_fc_digital_twin
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PowerBI Integration (Optional)
POWERBI_CLIENT_ID=your_powerbi_client_id
POWERBI_CLIENT_SECRET=your_powerbi_client_secret
POWERBI_TENANT_ID=your_powerbi_tenant_id
POWERBI_WORKSPACE_ID=your_powerbi_workspace_id
```

### 5. Database Setup

```bash
# Create database (PostgreSQL)
createdb chelsea_fc_digital_twin

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)

```bash
# Generate sample data for testing
python manage.py shell -c "
from operations.generate_sample_data import generate_sample_data
generate_sample_data()
"
```

### 7. Create Required Directories

```bash
mkdir -p operations/logs
mkdir -p operations/exports
mkdir -p media
mkdir -p staticfiles
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the Chelsea FC Digital Twin platform!

### 10. Access the Football Field Visualization

Once the server is running:
1. Navigate to `http://localhost:8000`
2. Login with your superuser credentials
3. Click on "Football Field" in the main navigation
4. Enjoy the interactive football field visualization!

## 🔧 Additional Setup Options

### Redis Setup (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Redis Setup (macOS with Homebrew)

```bash
brew install redis
brew services start redis
```

### PostgreSQL Setup (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database user
sudo -u postgres createuser --interactive
sudo -u postgres createdb chelsea_fc_digital_twin
```

### PostgreSQL Setup (macOS with Homebrew)

```bash
brew install postgresql
brew services start postgresql
createuser --interactive
createdb chelsea_fc_digital_twin
```

## 🎨 Features Available

- **Main Dashboard**: Clean Chelsea FC branded interface
- **Football Field Visualization**: Interactive top-down field view
- **Player Management**: Track player statistics and positions
- **Formation Analysis**: Visualize and analyze different formations
- **Match Analytics**: Comprehensive match analysis tools
- **Data Export**: Export to PowerBI, Excel, CSV formats
- **Live Tracking**: Real-time match tracking capabilities

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env` file
   - Verify database exists

2. **Redis Connection Error**
   - Ensure Redis server is running
   - Check Redis URL in `.env` file

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATICFILES_DIRS` settings

4. **Permission Errors**
   - Ensure proper file permissions
   - Create required directories manually

### Performance Optimization

For production deployment:

```bash
# Install additional production dependencies
pip install gunicorn whitenoise

# Use production settings
export DJANGO_SETTINGS_MODULE=config.production

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📊 Development Tools

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core

# Run specific tests
pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
black .

# Check imports
isort .

# Lint code
flake8 .
```

### Database Management

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

## 🚀 Deployment

For production deployment, consider:

- Use environment variables for sensitive data
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use a production database
- Set up proper logging
- Configure static file serving
- Use HTTPS
- Set up monitoring and alerts

## 📞 Support

If you encounter any issues:

1. Check the logs in `operations/logs/`
2. Ensure all requirements are properly installed
3. Verify environment configuration
4. Check database and Redis connectivity

## 🎯 Next Steps

After setup:

1. Explore the main dashboard
2. Check out the interactive football field
3. Import your team data
4. Set up formations and player positions
5. Start tracking matches and performance

Happy analyzing! 🏆⚽