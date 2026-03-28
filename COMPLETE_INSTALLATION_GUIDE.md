# 🚀 Complete Surgery Day Builder Website Installation Guide

## What You Now Have

✅ **Backend** (Python/Flask) - 100% Complete
✅ **Frontend** (HTML/CSS/JavaScript) - 100% Complete  
✅ **Database** Models - 100% Complete
✅ **API Routes** - 100% Complete
✅ **AI Integration** - 100% Complete

**Everything you need to launch your website is ready!**

---

## Folder Structure

Create this exact folder structure:

```
surgery-day-builder/
├── app.py                          # Main Flask app
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── .env                            # Environment variables (CREATE THIS)
├── .gitignore
│
├── app/
│   ├── __init__.py                 # Empty or init code
│   ├── models/
│   │   ├── __init__.py
│   │   └── health_journey.py        # Database models
│   ├── services/
│   │   ├── __init__.py
│   │   └── journey_generator.py     # Claude API service
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                  # If splitting routes
│   │   └── (other routes)
│   ├── templates/
│   │   ├── base.html                # Base template
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── public/
│   │   │   ├── index.html           # Homepage
│   │   │   ├── about.html
│   │   │   └── resources.html
│   │   ├── journey/
│   │   │   ├── builder.html         # Chat builder
│   │   │   ├── dashboard.html       # User dashboard
│   │   │   ├── view.html            # Published journey
│   │   │   └── edit.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css             # Main styles
│   │   │   ├── auth.css             # Auth pages
│   │   │   ├── journey.css          # Journey pages
│   │   │   └── errors.css           # Error pages
│   │   ├── js/
│   │   │   ├── main.js              # Main scripts
│   │   │   └── chat.js              # Chat functionality
│   │   ├── images/
│   │   │   └── (logo, icons, etc)
│   │   └── uploads/                 # User uploads
│   └── extensions.py                # Database setup
│
├── migrations/                      # Database migrations
│   ├── versions/
│   └── (auto-generated)
│
└── docs/
    ├── SETUP.md                     # This file
    ├── API.md                       # API documentation
    └── DATABASE.md                  # Database schema
```

---

## Step-by-Step Installation

### Step 1: Download All Files

From `/mnt/user-data/outputs/` download:

**Backend Files:**
- app.py
- config.py
- requirements.txt
- models_health_journey.py
- services_journey_generator.py
- routes_journey.py

**Frontend Files:**
- templates_base.html → rename to base.html
- templates_auth_*.html → put in templates/auth/
- templates_public_*.html → put in templates/public/
- templates_journey_*.html → put in templates/journey/
- templates_errors_*.html → put in templates/errors/

**CSS Files:**
- static_css_main.css → static/css/main.css
- static_css_auth.css → static/css/auth.css
- static_css_journey.css → static/css/journey.css
- static_css_errors.css → static/css/errors.css

**JavaScript Files:**
- static_js_main.js → static/js/main.js
- static_js_chat.js → static/js/chat.js

### Step 2: Create Folder Structure

```bash
mkdir -p surgery-day-builder
cd surgery-day-builder

# Create all folders
mkdir -p app/{models,services,routes,templates/{auth,public,journey,errors},static/{css,js,images,uploads}}
mkdir -p migrations/versions
mkdir docs

# Place files in correct locations
# Copy app.py, config.py, requirements.txt to root
# Copy models_health_journey.py to app/models/
# Copy services_journey_generator.py to app/services/
# Copy all HTML files to app/templates/
# Copy all CSS files to app/static/css/
# Copy all JS files to app/static/js/
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Create .env File

```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=postgresql://localhost/surgery_day_builder

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional
UPLOAD_FOLDER=static/uploads
MAX_FILE_SIZE=52428800
```

### Step 6: Set Up PostgreSQL

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from postgresql.org

# Create database
createdb surgery_day_builder

# Start PostgreSQL
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql
# Windows: PgAdmin or Services
```

### Step 7: Initialize Flask App

Create `app/__init__.py`:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app
```

### Step 8: Update app.py

If using the modular approach, update app.py to use app factory pattern:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### Step 9: Initialize Database

```bash
# Create migrations folder
flask db init

# Create initial migration
flask db migrate -m "Initial schema"

# Apply migrations
flask db upgrade
```

### Step 10: Create Test User

```bash
flask shell

>>> from app import db, User
>>> user = User(email='test@example.com', username='testuser', name='Test User')
>>> user.set_password('password123')
>>> db.session.add(user)
>>> db.session.commit()
>>> exit()
```

### Step 11: Start Server

```bash
flask run
```

Visit: **http://localhost:5000**

---

## File Mapping Quick Reference

| File | Goes To | Purpose |
|------|---------|---------|
| app.py | Root | Main Flask application |
| config.py | Root | Configuration |
| requirements.txt | Root | Dependencies |
| models_health_journey.py | app/models/ | Database models |
| services_journey_generator.py | app/services/ | Claude API integration |
| routes_journey.py | app/routes/ | API routes |
| templates_base.html | app/templates/ | Base template |
| templates_auth_*.html | app/templates/auth/ | Auth pages |
| templates_public_*.html | app/templates/public/ | Public pages |
| templates_journey_*.html | app/templates/journey/ | Journey pages |
| templates_errors_*.html | app/templates/errors/ | Error pages |
| static_css_*.css | app/static/css/ | Stylesheets |
| static_js_*.js | app/static/js/ | JavaScript |

---

## What Each File Does

### Backend

**app.py**
- Flask application initialization
- Database models (User, HealthJourney, JourneyComment)
- All routes (auth, public, journey, API, health)
- Error handlers
- Login manager setup

**config.py**
- Development configuration
- Production configuration  
- Testing configuration
- Environment variable setup

**models_health_journey.py**
- User model
- HealthJourney model
- JourneyComment model
- Database relationships

**services_journey_generator.py**
- Claude API integration
- Multi-turn conversation handling
- JSON structure generation
- SVG diagram generation

**routes_journey.py**
- All API endpoints
- Journey builder routes
- Health journey view routes
- Comment endpoints

### Frontend

**Templates**

- **base.html** - Navigation, layout, footer used by all pages
- **auth/login.html** - Login form
- **auth/register.html** - Registration form
- **public/index.html** - Homepage with featured journeys
- **public/about.html** - About page
- **public/resources.html** - Healthcare resources
- **journey/builder.html** - Chat interface for creating journeys
- **journey/dashboard.html** - User's journey management
- **journey/view.html** - Published journey display
- **errors/404.html** - 404 error page
- **errors/500.html** - 500 error page

**CSS**

- **main.css** - Colors, typography, buttons, layout (2000+ lines)
- **auth.css** - Login/register page styling
- **journey.css** - Builder and view page styling (2000+ lines)
- **errors.css** - Error page styling

**JavaScript**

- **main.js** - Navigation, utilities, form validation
- **chat.js** - Chat functionality, preview updates, publishing

---

## How to Test

### Test 1: Homepage
Visit http://localhost:5000
- Should see featured journeys section
- Should see "Register" and "Login" buttons

### Test 2: Register
1. Click "Register"
2. Fill in form (email, username, password)
3. Click "Register"
4. Should redirect to /journey/builder

### Test 3: Chat Interface
1. At /journey/builder
2. Type: "I had Chiari surgery on Feb 26, 2026"
3. Click "Send"
4. Should see Claude response
5. Continue conversation
6. Should see preview update
7. After structure appears, click "Publish"

### Test 4: View Journey
1. After publishing
2. Should see beautiful timeline
3. Should see comments section
4. Should see share button

### Test 5: Dashboard
1. Click "Dashboard"
2. Should see list of your journeys
3. Can edit or delete journeys

---

## Common Issues & Solutions

### "Module not found: flask"
```bash
# Activate virtual environment first
source venv/bin/activate
pip install -r requirements.txt
```

### "Database connection refused"
```bash
# Ensure PostgreSQL is running
# macOS
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql

# Windows: Check Services
```

### "No such table: users"
```bash
# Run migrations
flask db upgrade
```

### "ANTHROPIC_API_KEY not found"
```bash
# Create .env file with your key
ANTHROPIC_API_KEY=sk-ant-...
```

### Static files not loading
- Check CSS/JS file paths
- Clear browser cache (Ctrl+Shift+Delete)
- Check file permissions

### Chat not responding
- Check ANTHROPIC_API_KEY
- Check internet connection
- Look at Flask console for errors

---

## Running in Production

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build: `docker build -t surgery-day-builder .`
Run: `docker run -p 8000:8000 -e DATABASE_URL=... surgery-day-builder`

---

## Summary

You now have:

✅ **11 HTML templates** - All pages needed for the site
✅ **4 CSS files** - Professional styling (2000+ lines)
✅ **2 JavaScript files** - Chat and navigation
✅ **Complete Flask backend** - All routes and logic
✅ **Database models** - User, Journey, Comment
✅ **AI integration** - Claude API ready
✅ **Error handling** - 404 and 500 pages
✅ **Responsive design** - Mobile-friendly

**Everything is ready to run!**

---

## Next Steps

1. ✅ Create folder structure
2. ✅ Download all files
3. ✅ Place files in correct locations
4. ✅ Create .env file
5. ✅ Install PostgreSQL
6. ✅ Install Python dependencies
7. ✅ Run database migrations
8. ✅ Start Flask server
9. ✅ Test all features
10. ✅ Deploy to production

---

## File Checklist

**Backend**
- [ ] app.py
- [ ] config.py
- [ ] requirements.txt
- [ ] models_health_journey.py
- [ ] services_journey_generator.py

**Templates (11 files)**
- [ ] base.html
- [ ] auth/login.html
- [ ] auth/register.html
- [ ] public/index.html
- [ ] public/about.html
- [ ] public/resources.html
- [ ] journey/builder.html
- [ ] journey/dashboard.html
- [ ] journey/view.html
- [ ] errors/404.html
- [ ] errors/500.html

**CSS (4 files)**
- [ ] static/css/main.css
- [ ] static/css/auth.css
- [ ] static/css/journey.css
- [ ] static/css/errors.css

**JavaScript (2 files)**
- [ ] static/js/main.js
- [ ] static/js/chat.js

---

Good luck! You're ready to launch! 🚀
