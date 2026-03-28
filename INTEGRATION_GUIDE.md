# Surgery Day Builder - Integration Guide

## Quick Start for Joe & Jonah

This guide explains how to integrate the Surgery Day Builder system into your existing Peck's Mission Flask app.

---

## File Structure

Copy/create these files in your project:

```
pecksmission/
├── app/
│   ├── models/
│   │   └── health_journey.py          # NEW - Database models
│   ├── services/
│   │   └── journey_generator.py       # NEW - Claude AI integration
│   ├── routes/
│   │   └── journey.py                 # NEW - Flask routes
│   └── extensions.py                  # EXISTING - Database setup
├── templates/
│   └── journey/
│       ├── builder.html               # NEW - Chat interface
│       └── view.html                  # NEW - Published journey page
├── static/
│   └── css/
│       └── journey.css                # NEW - Styles (optional, CSS is inline)
└── requirements.txt                   # UPDATE - Add anthropic
```

---

## Step 1: Install Dependencies

Add to `requirements.txt`:
```
anthropic>=0.25.0  # Claude API
```

Install:
```bash
pip install anthropic
```

---

## Step 2: Create Database Models

Create `app/models/health_journey.py`:

```python
from app.extensions import db
from datetime import datetime
import uuid
import enum

class JourneyStatus(enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    DRAFT = "draft"

class JourneyPrivacy(enum.Enum):
    PUBLIC = "public"
    SEMI_PRIVATE = "semi-private"
    PRIVATE = "private"

class HealthJourney(db.Model):
    __tablename__ = 'health_journeys'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Metadata
    title = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(255))
    procedure_type = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.Enum(JourneyStatus), default=JourneyStatus.DRAFT)
    summary = db.Column(db.Text)
    
    # AI-generated content
    stages = db.Column(db.JSON, default=[])
    timeline_entries = db.Column(db.JSON, default=[])
    color_scheme = db.Column(db.JSON, default={})
    
    # Privacy
    privacy = db.Column(db.Enum(JourneyPrivacy), default=JourneyPrivacy.PRIVATE)
    share_token = db.Column(db.String(255), unique=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Media
    gallery_photos = db.Column(db.JSON, default=[])
    videos = db.Column(db.JSON, default=[])
    diagrams = db.Column(db.JSON, default=[])
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship("User", back_populates="health_journeys")
    comments = db.relationship("JourneyComment", back_populates="journey", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthJourney {self.slug}: {self.title}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': str(self.id),
            'slug': self.slug,
            'title': self.title,
            'condition': self.condition,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'stages': self.stages,
            'timeline_entries': self.timeline_entries,
            'color_scheme': self.color_scheme,
            'privacy': self.privacy.value,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
        }

class JourneyComment(db.Model):
    __tablename__ = 'journey_comments'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('health_journeys.id', ondelete='CASCADE'), nullable=False)
    
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255))
    comment = db.Column(db.Text, nullable=False)
    reactions = db.Column(db.JSON, default=[])
    
    is_approved = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    journey = db.relationship("HealthJourney", back_populates="comments")
    
    def __repr__(self):
        return f"<JourneyComment by {self.user_name}>"

# Add relationship to User model:
# In app/models/user.py, add:
# health_journeys = db.relationship("HealthJourney", back_populates="user", cascade="all, delete-orphan")
```

Create migration:
```bash
flask db migrate -m "Add HealthJourney and JourneyComment models"
flask db upgrade
```

---

## Step 3: Create Journey Generator Service

Create `app/services/journey_generator.py` with the code from `services_journey_generator.py` above.

Set environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or add to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Load in `app/__init__.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
```

---

## Step 4: Create Routes

Create `app/routes/journey.py` with the code from `routes_journey.py` above.

Update `app/__init__.py` or your main `app.py`:
```python
from app.routes.journey import register_journey_routes

def create_app():
    app = Flask(__name__)
    # ... other setup ...
    register_journey_routes(app)
    return app
```

---

## Step 5: Create Templates

Create these template files:

**`templates/journey/builder.html`**
Copy the code from `templates_journey_builder.html`

**`templates/journey/view.html`**
Copy the code from `templates_journey_view.html`

---

## Step 6: Update Your User Model

In `app/models/user.py`, add:
```python
class User(db.Model):
    # ... existing fields ...
    
    # New relationship for journeys
    health_journeys = db.relationship(
        "HealthJourney", 
        back_populates="user", 
        cascade="all, delete-orphan",
        foreign_keys="HealthJourney.user_id"
    )
```

---

## Step 7: Update Navigation

Add link to Surgery Day Builder in your main navigation:

```html
<!-- In base template or navigation -->
<a href="/journey/builder">Create Your Journey</a>
```

---

## Step 8: Test Locally

```bash
# Start Flask app
flask run

# Visit http://localhost:5000/journey/builder
# Start a conversation like:
# "I had Chiari surgery on February 26, 2026. Recovery took 6 weeks."
```

---

## API Endpoints Summary

### User-Facing Routes:
- `GET /journey/builder` - Chat interface
- `GET /health-journey/<slug>` - View published journey
- `GET /journey/dashboard` - User's journeys (requires login)

### API Endpoints:
- `POST /api/journey/chat` - Process chat message
- `POST /api/journey` - Create journey from structure
- `PUT /api/journey/<id>` - Update journey
- `DELETE /api/journey/<id>` - Delete journey
- `POST /api/journey/<id>/share` - Share with email
- `GET /api/journey/<id>/comments` - Get comments
- `POST /api/journey/<id>/comments` - Add comment
- `POST /api/journey/<id>/comments/<comment_id>/react` - Add reaction

---

## Configuration

Add to your `.env` or config:

```python
# Journey Configuration
JOURNEY_MAX_ENTRIES = 50
JOURNEY_MAX_PHOTOS = 100
JOURNEY_MAX_VIDEO_SIZE_MB = 500

# Claude API
ANTHROPIC_API_KEY = "sk-ant-..."
CLAUDE_MODEL = "claude-opus-4-20250805"

# S3 (if using media upload)
AWS_ACCESS_KEY_ID = "..."
AWS_SECRET_ACCESS_KEY = "..."
S3_BUCKET_NAME = "pecksmission-journeys"
S3_REGION = "us-east-1"
```

---

## Features by Phase

### Phase 1 (MVP) - Done
- ✅ Chat interface for journey creation
- ✅ AI generates journey structure
- ✅ Publish to public URL
- ✅ View journey timeline

### Phase 2 - Soon
- [ ] AI generates timeline entries
- [ ] AI generates color schemes
- [ ] AI generates SVG diagrams

### Phase 3
- [ ] Photo upload with captions
- [ ] Video integration

### Phase 4
- [ ] Share with privacy levels
- [ ] Embed code
- [ ] Email sharing

### Phase 5
- [ ] Comments
- [ ] Reactions (heart, hug, encouragement, celebrate)
- [ ] Moderation

---

## Testing Checklist

- [ ] Create journey via chat
  - [ ] AI asks clarifying questions
  - [ ] Journey structure extracted
  - [ ] Publish button appears
  
- [ ] View published journey
  - [ ] All sections render
  - [ ] Responsive on mobile
  - [ ] Share button works
  
- [ ] Comments & reactions
  - [ ] Can post comment
  - [ ] Can react to comment
  - [ ] Comment appears immediately
  
- [ ] Privacy
  - [ ] Public journeys searchable
  - [ ] Private journeys require share_token
  - [ ] Semi-private requires login

---

## Future Enhancements

1. **Condition Templates** - Pre-built stages for common procedures
   - Chiari: "Pre-op → Surgery → ICU Recovery → Home Recovery → PT → Return to Normal"
   - Cancer: "Diagnosis → Surgery/Chemo → Recovery → Follow-up"

2. **AI Refinement** - Ask Claude to revise entries
   - "Make the surgery day entry more emotional"
   - "Add more about my faith journey"

3. **PDF Export** - Convert journey to downloadable PDF

4. **Integration with Resources** - Link public journeys to condition-specific resource pages

5. **Analytics** - Track views, shares, comments per journey

6. **Community Dashboard** - Feature public journeys by condition

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check `.env` file has the key
- Check `load_dotenv()` is called in `app/__init__.py`
- Restart Flask dev server

### "Claude API rate limit"
- Wait a few seconds and try again
- In production, implement request queuing

### Database migrations fail
- Drop the tables: `flask db downgrade`
- Re-create: `flask db upgrade`
- Or: `flask db stamp head && flask db upgrade`

### Journey not publishing
- Check user is logged in
- Check `user_id` is set correctly
- Check database connection

---

## Integration with Existing Features

### Blog Integration
Add journeys to blog listing:

```python
# In app/routes/public.py (blog listing)
from app.models import HealthJourney

@app.route('/blog')
def blog():
    # Get public journeys
    journeys = HealthJourney.query.filter_by(
        privacy='public',
        is_deleted=False
    ).order_by(HealthJourney.created_at.desc()).limit(10)
    
    # Mix with regular posts
    all_content = list(posts) + list(journeys)
    all_content.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('blog.html', posts=all_content)
```

### User Dashboard
Show in user's journey dashboard:

```python
# /user/journeys
journeys = current_user.health_journeys
```

### Resources Integration
Link condition-specific journeys to resources:

```python
# In /resources/topics/[condition]
# Show featured public journeys about that condition
public_journeys = HealthJourney.query.filter_by(
    condition=condition,
    privacy='public'
).order_by(HealthJourney.view_count.desc()).limit(5)
```

---

## Database Schema (SQL)

```sql
CREATE TABLE health_journeys (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    condition VARCHAR(255),
    procedure_type VARCHAR(255),
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'draft',
    summary TEXT,
    stages JSONB DEFAULT '[]',
    timeline_entries JSONB DEFAULT '[]',
    color_scheme JSONB DEFAULT '{}',
    privacy VARCHAR(50) DEFAULT 'private',
    share_token VARCHAR(255),
    is_published BOOLEAN DEFAULT false,
    gallery_photos JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    diagrams JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false
);

CREATE TABLE journey_comments (
    id UUID PRIMARY KEY,
    journey_id UUID NOT NULL REFERENCES health_journeys(id) ON DELETE CASCADE,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    comment TEXT NOT NULL,
    reactions JSONB DEFAULT '[]',
    is_approved BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_journey_user_id ON health_journeys(user_id);
CREATE INDEX idx_journey_slug ON health_journeys(slug);
CREATE INDEX idx_journey_privacy ON health_journeys(privacy);
CREATE INDEX idx_comment_journey_id ON journey_comments(journey_id);
```

---

## Questions?

- Where do you want to store uploads? (S3, local filesystem, etc.)
- Should all comments require approval before appearing?
- Do you want email notifications when someone comments?
- Should journeys be listed on the homepage?

---

## Next Steps for Joe & Jonah

1. **Joe**: Test the chat interface, refine AI prompts
2. **Jonah**: Integrate into Flask app, set up database, test routes
3. **Both**: User test with 3-5 people, iterate on UX
4. **Deploy**: Get feedback from Surgery Day users, iterate

Good luck! 🚀

