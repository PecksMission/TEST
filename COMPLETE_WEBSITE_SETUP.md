# Surgery Day Builder - Complete Website Setup

## Project Structure

```
surgery-day-builder/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (CREATE THIS)
├── .gitignore                      # Git ignore file
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── health_journey.py       # Database models
│   ├── services/
│   │   ├── __init__.py
│   │   └── journey_generator.py    # Claude API service
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication routes
│   │   ├── public.py               # Public routes (home, about, resources)
│   │   ├── journey.py              # Journey builder routes
│   │   └── health.py               # Health journey view routes
│   ├── templates/
│   │   ├── base.html               # Base template
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── reset_password.html
│   │   ├── public/
│   │   │   ├── index.html          # Homepage
│   │   │   ├── about.html
│   │   │   └── resources.html
│   │   ├── journey/
│   │   │   ├── builder.html        # Chat interface
│   │   │   ├── dashboard.html      # User's journeys
│   │   │   ├── view.html           # Published journey
│   │   │   ├── edit.html
│   │   │   └── share.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   ├── auth.css
│   │   │   ├── journey.css
│   │   │   └── responsive.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── chat.js
│   │   │   ├── journey.js
│   │   │   └── forms.js
│   │   ├── images/
│   │   │   └── logo.svg
│   │   └── uploads/                # User uploaded files
│   └── extensions.py               # Database, login manager setup
│
├── migrations/                     # Database migrations (auto-generated)
│
└── docs/
    ├── SETUP.md                    # Setup instructions
    ├── API.md                      # API documentation
    └── DATABASE.md                 # Database schema

```

---

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/surgery-day-builder.git
cd surgery-day-builder
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/surgery_day_builder

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# File uploads
UPLOAD_FOLDER=static/uploads
MAX_FILE_SIZE=52428800  # 50MB in bytes

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_REGION=us-east-1

# Redis (optional, for session storage)
REDIS_URL=redis://localhost:6379/0

# Email (optional, for notifications)
MAIL_SERVER=
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
```

### 5. Set Up Database

```bash
# Install PostgreSQL if needed
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from postgresql.org

# Create database
createdb surgery_day_builder

# Create migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user (optional)
flask shell
>>> from app import User, db
>>> admin = User(email='admin@example.com', username='admin', name='Admin')
>>> admin.set_password('admin-password')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

### 6. Run Development Server
```bash
flask run
```

Then visit: http://localhost:5000

---

## File Descriptions

### `app.py`
Main Flask application file. Contains:
- App configuration
- Database models (User, HealthJourney, JourneyComment)
- All routes (auth, public, journey, API)
- Error handlers
- Login manager setup

### `config.py` (Create this)
```python
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 52428800))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### `requirements.txt` (Create this)
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.2
psycopg2-binary==2.9.7
python-dotenv==1.0.0
anthropic==0.7.1
boto3==1.28.17  # For S3
redis==5.0.0    # For sessions
gunicorn==21.2.0  # For production
```

---

## Route Map

### Public Routes
- `GET /` - Homepage
- `GET /about` - About page
- `GET /resources` - Healthcare resources
- `GET /health-journey/<slug>` - View published journey
- `GET /health-journey/<slug>/share` - Share page

### Authentication Routes
- `GET/POST /auth/register` - Register account
- `GET/POST /auth/login` - Login
- `GET /auth/logout` - Logout

### Journey Routes (Require Login)
- `GET /journey/builder` - Chat interface for creating journeys
- `GET /journey/dashboard` - User's journeys
- `GET /journey/<id>/edit` - Edit journey

### API Routes (JSON)
- `POST /api/journey/chat` - Process chat message
- `POST /api/journey` - Create journey
- `GET/POST /api/journey/<id>/comments` - Get/add comments
- `POST /api/journey/<id>/upload-photo` - Upload photo

---

## Database Schema

### users table
```sql
- id (UUID, PK)
- email (String, unique)
- username (String, unique)
- password_hash (String)
- name (String)
- bio (Text)
- avatar_url (String)
- created_at, updated_at
- is_active (Boolean)
```

### health_journeys table
```sql
- id (UUID, PK)
- user_id (FK to users)
- slug (String, unique)
- title, condition, procedure_type
- start_date, end_date
- status (draft/active/completed)
- summary (Text)
- stages (JSON)
- timeline_entries (JSON)
- color_scheme (JSON)
- privacy (public/semi-private/private)
- share_token (String)
- is_published (Boolean)
- gallery_photos (JSON)
- videos (JSON)
- diagrams (JSON)
- view_count (Integer)
- created_at, updated_at
- is_deleted (Boolean)
```

### journey_comments table
```sql
- id (UUID, PK)
- journey_id (FK to health_journeys)
- user_name (String)
- user_email (String)
- comment (Text)
- reactions (JSON)
- is_approved (Boolean)
- is_deleted (Boolean)
- created_at, updated_at
```

---

## User Flow

### 1. New User
```
Visit site → Register → Create account → Redirect to builder
```

### 2. Create Journey
```
Visit /journey/builder
→ Chat with Claude about health journey
→ Describe condition, dates, milestones
→ Claude asks follow-up questions
→ AI generates journey structure
→ Review and click "Publish"
→ Journey saved to database
→ Get shareable link
```

### 3. View Journey
```
Owner views: /health-journey/slug (full access)
Anonymous visits public: /health-journey/slug (read-only)
Anonymous visits semi-private: Redirect to login
Private + correct share token: /health-journey/slug?share_token=xxx
```

### 4. Community Engagement
```
Visitor reads journey
→ Scrolls to comments section
→ Enters name and comment
→ Posts comment
→ Can add emoji reactions
→ Share journey via link/embed
```

---

## Key Features Implemented

✅ User authentication (register, login, logout)
✅ Journey creation with AI chat
✅ Journey publishing with privacy controls
✅ Journey viewing with timeline display
✅ Comments and reactions
✅ Photo uploads
✅ Share tokens for private journeys
✅ User dashboard with journeys
✅ Error handling
✅ Database migrations
✅ API endpoints

---

## What Each File Does

### Backend (Already Created)
- **app.py** - Main Flask app with all routes
- **services/journey_generator.py** - Claude API integration
- **models/health_journey.py** - Database models

### Frontend (Need to Create)
- **templates/base.html** - Base template with navigation
- **templates/auth/login.html** - Login form
- **templates/auth/register.html** - Registration form
- **templates/public/index.html** - Homepage
- **templates/journey/builder.html** - Chat interface
- **templates/journey/view.html** - Published journey
- **static/css/main.css** - Styles
- **static/js/chat.js** - Chat functionality

---

## Running in Production

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t surgery-day-builder .
docker run -p 8000:8000 -e DATABASE_URL=... surgery-day-builder
```

---

## Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Create `.env` file with your settings
4. ✅ Set up PostgreSQL database
5. ✅ Run database migrations
6. ✅ Start development server
7. ✅ Create templates (HTML files)
8. ✅ Test registration and login
9. ✅ Test journey creation
10. ✅ Deploy to production

---

## Troubleshooting

**Database connection error**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Check credentials

**Anthropic API error**
- Check ANTHROPIC_API_KEY in .env
- Verify key is valid
- Check internet connection

**Module not found**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**Static files not loading**
- Check STATIC_FOLDER path
- Clear browser cache
- Check file permissions

---

## Support

For issues or questions:
1. Check the documentation files
2. Review error logs
3. Check Flask debug messages
4. Look at database migrations

Good luck! 🚀
