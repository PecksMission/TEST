# DATA STORAGE GUIDE - Surgery Day Builder
## How to store user information, conversations, journeys, and media

This guide covers:
1. **Database storage** (PostgreSQL - structured data)
2. **File storage** (S3 or local - photos, videos)
3. **Session storage** (Flask/Redis - conversation history)
4. **Caching strategies** (Redis - performance)
5. **Data retention policy** (how long to keep data)

---

## PART 1: DATABASE SCHEMA

### TABLE 1: health_journeys (Main Journey Data)

```sql
CREATE TABLE health_journeys (
    id UUID PRIMARY KEY,                    -- Unique ID
    user_id UUID NOT NULL,                  -- Who created it
    slug VARCHAR(255) UNIQUE,               -- URL: /health-journey/my-surgery
    
    -- User Input
    title VARCHAR(255),                     -- "Chiari Surgery Recovery"
    condition VARCHAR(255),                 -- "Chiari Type I"
    procedure_type VARCHAR(255),            -- "Craniectomy"
    start_date DATE,                        -- When it started
    end_date DATE,                          -- When it ended (optional)
    
    -- AI-Generated Content (from Claude)
    summary TEXT,                           -- Brief description
    stages JSONB,                           -- Surgical stages
    timeline_entries JSONB,                 -- Daily entries
    color_scheme JSONB,                     -- {clinical, faith, family}
    
    -- Privacy & Sharing
    privacy VARCHAR(50),                    -- 'public', 'semi-private', 'private'
    share_token VARCHAR(255),               -- For private share links
    is_published BOOLEAN,                   -- Is it visible?
    
    -- Media
    gallery_photos JSONB,                   -- [{url, caption, date}, ...]
    videos JSONB,                           -- [{url, title}, ...]
    diagrams JSONB,                         -- [{svg, description}, ...]
    
    -- Status
    status VARCHAR(50),                     -- 'draft', 'active', 'completed'
    is_deleted BOOLEAN,                     -- Soft delete flag
    
    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**What gets stored here:**
- All journey metadata
- AI-generated structure (stages, entries)
- User profile data
- Privacy settings
- File references (URLs, not actual files)

**Size estimate:** 
- Per journey: ~5-50 KB (depends on number of entries)
- 1000 journeys: ~50 MB

### TABLE 2: journey_comments (Community Feedback)

```sql
CREATE TABLE journey_comments (
    id UUID PRIMARY KEY,
    journey_id UUID NOT NULL,               -- Which journey
    
    -- Commenter Info (public)
    user_name VARCHAR(255),                 -- Their name
    user_email VARCHAR(255),                -- Their email
    
    -- Comment
    comment TEXT,                           -- What they said
    reactions JSONB,                        -- [{type: 'heart', user_id, date}, ...]
    
    -- Moderation
    is_approved BOOLEAN,                    -- Approved by author?
    is_deleted BOOLEAN,                     -- Deleted?
    
    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**What gets stored here:**
- Visitor comments
- Emoji reactions (heart, hug, encouragement, celebration)
- Comment metadata

**Size estimate:**
- Per comment: ~500 bytes to 2 KB
- 100 comments: ~200 KB

---

## PART 2: WHAT DATA IS STORED IN JSON FIELDS

### stages (List of surgical phases)

```json
[
    {
        "name": "Pre-Surgery",
        "description": "Preparation and diagnosis",
        "color": "#5b8fa8",
        "duration_days": 7
    },
    {
        "name": "Surgery Day",
        "description": "Craniectomy procedure",
        "color": "#5b8fa8",
        "duration_days": 1
    },
    {
        "name": "Hospital Recovery",
        "description": "ICU stay and monitoring",
        "color": "#5b8fa8",
        "duration_days": 5
    },
    {
        "name": "Home Recovery",
        "description": "Healing at home",
        "color": "#a05c5c",
        "duration_days": 30
    }
]
```

### timeline_entries (Daily updates)

```json
[
    {
        "date": "2026-02-26",
        "type": "clinical",
        "title": "Surgery Day",
        "content": "Underwent craniectomy with duraplasty...",
        "media": []
    },
    {
        "date": "2026-02-27",
        "type": "faith",
        "title": "Gratitude",
        "content": "Blessed that the surgery went well...",
        "media": [
            {
                "type": "image",
                "url": "https://s3.amazonaws.com/journeys/uuid/photo.jpg",
                "caption": "First day post-op"
            }
        ]
    },
    {
        "date": "2026-03-01",
        "type": "family",
        "title": "Family Support",
        "content": "My family has been incredible...",
        "media": []
    }
]
```

### color_scheme (Visual styling)

```json
{
    "clinical": "#5b8fa8",      // Medical updates - blue
    "faith": "#a05c5c",          // Faith moments - burgundy
    "family": "#c9a84c",         // Family moments - gold
    "accent": "#c9a84c"          // Highlights - gold
}
```

### gallery_photos (User uploaded photos)

```json
[
    {
        "url": "https://s3.amazonaws.com/journeys/uuid/photo-1.jpg",
        "caption": "First walk after surgery!",
        "date": "2026-03-15",
        "alt_text": "Person walking in hallway",
        "size_bytes": 2048576
    },
    {
        "url": "https://s3.amazonaws.com/journeys/uuid/photo-2.jpg",
        "caption": "My surgical scar",
        "date": "2026-03-20",
        "alt_text": "Back of head with surgical scar",
        "size_bytes": 1536000
    }
]
```

### reactions (Emoji support)

```json
[
    {
        "type": "heart",
        "user_id": "user-123",
        "user_name": "Jane Doe",
        "created_at": "2026-03-15T10:30:00Z"
    },
    {
        "type": "encouragement",
        "user_id": "user-456",
        "user_name": "John Smith",
        "created_at": "2026-03-15T10:45:00Z"
    }
]
```

---

## PART 3: DATA FLOW DIAGRAM

```
USER STARTS CHAT (/journey/builder)
    ↓
    ├─ Session created: session_id = "abc-123"
    └─ Stored in: Flask session (temporary)
    
USER TYPES MESSAGE
    ↓
    ├─ "I had Chiari surgery February 26..."
    └─ Sent to: POST /api/journey/chat
    
BACKEND PROCESSES
    ↓
    ├─ Retrieve generator for session_id
    ├─ Add to conversation history (in memory)
    ├─ Call Claude API
    └─ Return response
    
RESPONSE RETURNED TO USER
    ↓
    ├─ "Tell me more about recovery..."
    ├─ Preview updated in browser
    └─ Stored in: Session (Flask memory)
    
CONVERSATION CONTINUES (repeat above)
    ↓
    ├─ User: "Recovery was 6 weeks..."
    ├─ Claude: "Any faith moments?"
    ├─ User: "Yes, my faith helped..."
    └─ Claude: *Generates complete structure*
    
CLAUDE GENERATES COMPLETE JOURNEY
    ↓
    ├─ Structure JSON created
    └─ Sent to: Browser display
    
USER CLICKS "PUBLISH JOURNEY"
    ↓
    ├─ POST /api/journey with complete data
    └─ Data includes: title, stages, entries, colors
    
BACKEND SAVES TO DATABASE
    ↓
    ├─ Create HealthJourney object
    ├─ Set all fields from Claude's output
    ├─ INSERT into health_journeys table
    ├─ db.session.commit()
    └─ Stored in: PostgreSQL
    
SESSION CLEANED UP
    ↓
    ├─ Delete session[session_id]
    ├─ Clear conversation history (was in memory)
    └─ Stored in: (nothing - cleared)
    
JOURNEY IS NOW PUBLISHED
    ↓
    ├─ Accessible at: /health-journey/chiari-surgery-recovery
    ├─ Data persisted in: PostgreSQL database
    └─ Stored in: health_journeys table
    
VISITORS CAN NOW INTERACT
    ↓
    ├─ View journey page
    ├─ Post comments → health_journey_comments table
    ├─ Add reactions → Update JSON in comments
    ├─ Upload photos → S3 + reference in DB
    └─ Share journey → Stored as share_token
```

---

## PART 4: WHERE TO STORE EACH DATA TYPE

| Data Type | Storage Location | Duration | Size |
|-----------|------------------|----------|------|
| Journey metadata | PostgreSQL table | Indefinite | ~1 KB |
| AI-generated content | PostgreSQL JSON field | Indefinite | ~5-50 KB |
| Comments | PostgreSQL table | Indefinite | ~500 B - 2 KB each |
| Reactions | PostgreSQL JSON field | Indefinite | ~100 B each |
| Chat conversation (active) | Flask session / Redis | 24 hours | ~2-10 KB |
| User input (typing) | Browser memory | Session only | ~1 KB |
| Photos | S3 or local `/static/uploads/` | Indefinite | 1-50 MB |
| Videos | S3 or local `/static/uploads/` | Indefinite | 50-500 MB |
| Thumbnails | S3 or local | Indefinite | ~100-500 KB |
| File URLs | PostgreSQL JSON field | Indefinite | ~200 B each |
| Cached journeys | Redis | 1 hour | ~10 KB |
| Session tokens | Redis | 24 hours | ~500 B |

---

## PART 5: FILE STORAGE OPTIONS

### OPTION A: Local File Storage

**Pros:**
- Free
- Simple to implement
- Full control over files
- Good for development

**Cons:**
- Doesn't scale
- Limited by disk space
- No CDN support
- Performance issues with large files

**Setup:**

```python
# In .env or config.py
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# In your route
import os
from werkzeug.utils import secure_filename

@app.route('/api/journey/<id>/upload-photo', methods=['POST'])
def upload_photo(id):
    file = request.files['file']
    
    # Validate
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    if not allowed_file(file.filename):
        return {'error': 'File type not allowed'}, 400
    
    # Create unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"journey-{id}-{time.time()}.{ext}"
    filename = secure_filename(filename)
    
    # Save
    filepath = os.path.join('static/uploads', filename)
    file.save(filepath)
    
    # Store in database
    journey = HealthJourney.query.get(id)
    photo = {
        'url': f'/static/uploads/{filename}',
        'caption': request.form.get('caption', ''),
        'date': datetime.now().isoformat()
    }
    
    if not journey.gallery_photos:
        journey.gallery_photos = []
    journey.gallery_photos.append(photo)
    db.session.commit()
    
    return {'success': True, 'photo': photo}, 201
```

### OPTION B: AWS S3 Cloud Storage

**Pros:**
- Scales to any size
- CDN support (fast delivery)
- Automatic backups
- Professional standard

**Cons:**
- Monthly cost (~$1-50 depending on usage)
- Requires AWS account
- More complex setup

**Setup:**

```python
# In .env
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
S3_BUCKET_NAME = "pecksmission-journeys"
S3_REGION = "us-east-1"

# In your route
import boto3

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('S3_REGION')
)

@app.route('/api/journey/<id>/upload-photo-s3', methods=['POST'])
def upload_photo_s3(id):
    file = request.files['file']
    
    # Create S3 path
    ext = file.filename.rsplit('.', 1)[1].lower()
    s3_key = f"journeys/{id}/photos/{time.time()}.{ext}"
    
    # Upload to S3
    s3_client.upload_fileobj(
        file,
        os.getenv('S3_BUCKET_NAME'),
        s3_key,
        ExtraArgs={'ContentType': file.content_type, 'ACL': 'public-read'}
    )
    
    # Build URL
    url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('S3_REGION')}.amazonaws.com/{s3_key}"
    
    # Store reference in database
    journey = HealthJourney.query.get(id)
    photo = {
        'url': url,
        's3_key': s3_key,
        'caption': request.form.get('caption', ''),
        'date': datetime.now().isoformat()
    }
    
    if not journey.gallery_photos:
        journey.gallery_photos = []
    journey.gallery_photos.append(photo)
    db.session.commit()
    
    return {'success': True, 'photo': photo}, 201
```

---

## PART 6: STORING CONVERSATION HISTORY

### During Chat (Temporary - Session/Redis)

While the user is creating their journey, the conversation history is stored **temporarily** in memory.

**Option A: Flask Session (Simple)**

```python
from flask import session

# When chat starts
session['journey_session_id'] = str(uuid.uuid4())
session['journey_sessions'] = {}

# When user sends message
session_id = session['journey_session_id']
if session_id not in session['journey_sessions']:
    session['journey_sessions'][session_id] = []

# After Claude responds
session['journey_sessions'][session_id].append({
    'turn': turn_number,
    'user_message': user_message,
    'ai_response': ai_response,
    'timestamp': datetime.utcnow().isoformat()
})

session.modified = True  # Important!
```

**Option B: Redis (Production)**

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# When chat starts
session_id = str(uuid.uuid4())
redis_client.setex(
    f"journey:session:{session_id}",
    3600,  # 1-hour expiry
    json.dumps({'conversation': []})
)

# After Claude responds
data = redis_client.get(f"journey:session:{session_id}")
conversation = json.loads(data)['conversation']

conversation.append({
    'turn': turn_number,
    'user': user_message,
    'assistant': ai_response,
    'timestamp': datetime.utcnow().isoformat()
})

redis_client.setex(
    f"journey:session:{session_id}",
    3600,
    json.dumps({'conversation': conversation})
)
```

### After Publishing (Permanent - Database)

Once the user clicks "Publish", the journey structure is saved to the **database** permanently.

```python
from app.extensions import db
from app.models import HealthJourney

journey = HealthJourney(
    user_id=current_user.id,
    slug=create_slug(journey_data['title']),
    title=journey_data['title'],
    condition=journey_data['condition'],
    stages=journey_data['stages'],  # Stored in JSON field
    timeline_entries=journey_data['timeline_entries'],  # Stored in JSON
    color_scheme=journey_data['color_scheme'],
    is_published=True,
    privacy='private'
)

db.session.add(journey)
db.session.commit()

# Clear session (conversation is done)
del session['journey_sessions'][session_id]
```

---

## PART 7: QUERYING DATA FROM DATABASE

### Get a specific journey

```python
journey = HealthJourney.query.filter_by(slug="chiari-surgery-recovery").first()

print(journey.title)           # "Chiari Surgery Recovery"
print(journey.stages)          # List of stages (JSON)
print(journey.timeline_entries)  # List of entries (JSON)
print(journey.gallery_photos)  # List of photos (JSON)
```

### Get all journeys by a user

```python
user_journeys = HealthJourney.query.filter_by(
    user_id=current_user.id,
    is_deleted=False
).order_by(HealthJourney.created_at.desc()).all()

for journey in user_journeys:
    print(f"{journey.title} - {journey.privacy}")
```

### Get public journeys (for homepage)

```python
public_journeys = HealthJourney.query.filter_by(
    privacy='public',
    is_deleted=False
).order_by(HealthJourney.created_at.desc()).limit(10).all()
```

### Get journeys by condition

```python
cancer_journeys = HealthJourney.query.filter(
    HealthJourney.condition.ilike('%cancer%'),
    HealthJourney.privacy == 'public'
).all()
```

### Get comments on a journey

```python
comments = JourneyComment.query.filter_by(
    journey_id=journey.id,
    is_deleted=False
).order_by(JourneyComment.created_at.desc()).all()

for comment in comments:
    print(f"{comment.user_name}: {comment.comment}")
```

---

## PART 8: EXAMPLE - COMPLETE FLOW

Here's the complete flow from user input to stored data:

```python
# 1. User visits /journey/builder
session_id = str(uuid.uuid4())
session['journey_session_id'] = session_id
session['journey_sessions'] = {session_id: {'conversation': []}}

# 2. User types: "I had Chiari surgery February 26, 2026"
user_message = "I had Chiari surgery February 26, 2026"

# 3. Send to Claude via JourneyGenerator
from services_journey_generator import JourneyGenerator
generator = JourneyGenerator()
result = generator.process_user_input(user_message)

# 4. Store response in session (temporary)
session['journey_sessions'][session_id]['conversation'].append({
    'user': user_message,
    'assistant': result['response'],
    'timestamp': datetime.utcnow().isoformat()
})

# 5. Continue conversation until complete
# ... (more turns) ...

# 6. Claude returns complete journey_structure
if result['journey_structure']:
    journey_data = result['journey_structure']
    
    # 7. User clicks "Publish"
    # 8. Save to database
    journey = HealthJourney(
        user_id=current_user.id,
        slug=create_slug(journey_data['title']),
        title=journey_data['title'],
        condition=journey_data['condition'],
        start_date=journey_data['start_date'],
        stages=journey_data['stages'],  # JSON field
        timeline_entries=journey_data['timeline_entries'],  # JSON field
        color_scheme=journey_data['color_scheme'],  # JSON field
        is_published=True,
        privacy='private',
        share_token=str(uuid.uuid4())
    )
    
    db.session.add(journey)
    db.session.commit()
    
    # 9. Clear session
    del session['journey_sessions'][session_id]
    
    # 10. Return URL
    return {
        'url': f'/health-journey/{journey.slug}',
        'journey_id': journey.id
    }
```

---

## PART 9: DATA RETENTION POLICY

### How long to keep data:

| Data Type | Duration | Action |
|-----------|----------|--------|
| Journey content | Indefinite | Keep forever (or until user deletes) |
| Comments | Indefinite | Keep forever |
| Chat conversation (during creation) | 24 hours | Auto-delete from Redis |
| Session data | 24 hours | Auto-delete |
| Temporary file uploads | 7 days | Delete if not published |
| File backups | 30 days | Delete old backups |

### Cleanup script (run daily via cron):

```python
from datetime import datetime, timedelta

def cleanup_old_sessions():
    """Delete old session data from Redis"""
    all_keys = redis_client.keys("journey:session:*")
    
    for key in all_keys:
        # Get TTL (time to live)
        ttl = redis_client.ttl(key)
        
        # If TTL is negative, key is expired - Redis auto-deletes
        if ttl < 0:
            redis_client.delete(key)

def cleanup_old_drafts():
    """Delete draft journeys not saved after 7 days"""
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    old_drafts = HealthJourney.query.filter(
        HealthJourney.status == 'draft',
        HealthJourney.updated_at < cutoff_date
    ).all()
    
    for draft in old_drafts:
        draft.is_deleted = True
    
    db.session.commit()

# Run via cron job:
# 0 2 * * * python /path/to/cleanup.py
```

---

## PART 10: SUMMARY TABLE

```
┌─────────────────────────┬──────────────────┬──────────────┬────────────┐
│ Data Type               │ Storage          │ Duration     │ Size       │
├─────────────────────────┼──────────────────┼──────────────┼────────────┤
│ Journey metadata        │ PostgreSQL       │ Indefinite   │ ~1 KB      │
│ Stages/entries          │ PostgreSQL JSON  │ Indefinite   │ ~5-50 KB   │
│ Color scheme            │ PostgreSQL JSON  │ Indefinite   │ ~200 B     │
│ Comments                │ PostgreSQL       │ Indefinite   │ ~500 B-2KB │
│ Reactions               │ PostgreSQL JSON  │ Indefinite   │ ~100 B     │
├─────────────────────────┼──────────────────┼──────────────┼────────────┤
│ Chat conversation       │ Redis/Session    │ 24 hours     │ ~2-10 KB   │
│ Session data            │ Flask/Redis      │ 24 hours     │ ~500 B     │
├─────────────────────────┼──────────────────┼──────────────┼────────────┤
│ Photos                  │ S3/Local         │ Indefinite   │ 1-50 MB    │
│ Videos                  │ S3/Local         │ Indefinite   │ 50-500 MB  │
│ Thumbnails              │ S3/Local         │ Indefinite   │ ~100-500KB │
│ File URLs               │ PostgreSQL JSON  │ Indefinite   │ ~200 B     │
├─────────────────────────┼──────────────────┼──────────────┼────────────┤
│ Cached journeys         │ Redis            │ 1 hour       │ ~10 KB     │
│ Temp uploads            │ Local disk       │ 7 days       │ Variable   │
└─────────────────────────┴──────────────────┴──────────────┴────────────┘
```

---

## NEXT STEPS

1. **Choose storage option:**
   - Local files for development
   - S3 for production

2. **Set up database:**
   - Run migrations
   - Create tables

3. **Configure file handling:**
   - Set UPLOAD_FOLDER
   - Set file size limits
   - Configure S3 (if using)

4. **Test the flow:**
   - Create a journey
   - Upload photos
   - Verify in database

5. **Monitor storage:**
   - Track database size
   - Monitor S3 costs
   - Clean up old data

