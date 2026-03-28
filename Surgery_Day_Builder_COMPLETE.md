# Surgery Day Builder — Complete Specification
## All Information Combined

---

## PART 1: ORIGINAL SURGERY DAY ARCHITECTURE

### Source Files & Routes
```python
# Flask route: app/routes/public.py:168-175
@public_bp.route('/surgery-day')
def surgery_day():
    root = os.path.dirname(current_app.root_path)
    return send_from_directory(root, 'surgery-day.html')

@public_bp.route('/surgery-day.html')
def surgery_day_redirect():
    return redirect(url_for('public.surgery_day'), 301)
```

```nginx
# deploy/nginx.conf:41-44
301 redirect from /surgery-day.html → /surgery-day
```

### File Structure
- `/surgery-day.html` — 2,732-line standalone HTML file (not Flask template)
- Located in project root
- All CSS inline (no external stylesheets)
- All JS inline (no bundler/framework)
- External CDNs: Firebase Firestore, Mailchimp, Google Analytics

### Design System
```css
/* Color Tokens */
--black: #181b1e (background)
--white: #e8e3d8 (text)
--gold: #c9a84c (primary accent, family tag color)
--clinical: #5b8fa8 (clinical updates tag)
--faith: #a05c5c (faith entries tag)

/* Typography */
Bebas Neue (headings, large & bold)
Crimson Pro (body text, reading)
DM Mono (labels, metadata, timestamps)
```

### Page Structure (Linear, Top to Bottom)
1. **Fixed Navigation Bar** (hamburger menu, responsive 768px breakpoint)
2. **Page Header Section**
   - Eyebrow text ("Surgery Day / Recovery Timeline")
   - Main title (patient name or journey title)
   - Metadata (date range, location, condition)
   - Legend (Clinical/Faith/Family color key)
3. **Progress Board** (7 surgical stages)
   - Each stage: colored dot + name + brief description
   - Horizontal layout, responsive to grid
4. **Timeline** (main content)
   - Chronological entries (Feb 26 – Mar 4, 2026)
   - Each entry: date, type (clinical/faith/family), title, content, optional media
   - Color-coded by type (clinical=blue, faith=rose, family=gold)
5. **SVG Medical Diagrams** (3-step procedure explanation)
   - Step 1: Craniectomy (skull removal)
   - Step 2: Laminectomy (vertebra removal)
   - Step 3: Duraplasty (membrane repair)
   - Clean, labeled, educational
6. **Photo Gallery** (with captions)
   - WebP format images
   - Post-op walk, scar, medications, discharge docs, walking recovery
   - Responsive grid layout
7. **Comments Section** (Firebase Firestore)
   - Real-time comments
   - Reactions: heart, hug, encouragement, celebration
   - localStorage "salute" system (thumbs up)
   - Show comment count
8. **Mailchimp Email Signup** (popup fires after 60s)
   - CTA to subscribe to updates
   - Styled with brand colors

### Firebase Configuration
```javascript
{
  projectId: "joes-mission",
  authDomain: "joes-mission.firebaseapp.com",
  storageBucket: "joes-mission.firebasestorage.app",
  databaseURL: "https://joes-mission.firebaseio.com"
}

// Firestore collection: /surgery-day/comments
// Each doc: {name, email, comment, reactions, timestamp}
```

### Media Assets
- `post-surgery-walk.mov` (22 MB, post-op walk video)
- `scar.webp` (2.5 MB, surgical scar photo)
- `meds.webp` (1.6 MB, post-op medications)
- `discharge.webp` (395 KB, discharge documents)
- `walk.webp` (9.8 MB, walking recovery)

### Analytics
- Google Analytics ID: `G-WT1126YN2Q`
- Surgery Day hard-coded in blog listing (`public.py:135-159`)
- Tracked as synthetic entry: `views: 1891`, `tag: Surgery`

---

## PART 2: AI-POWERED SURGERY DAY BUILDER

### Vision
Create a system where any user can generate a personalized Surgery Day-like timeline by describing their health journey to an AI. System handles structure, design, and page generation automatically.

### User Flow (5 Steps)

#### Step 1: Entry Point
- URL: `/surgery-day-builder` (public, no login required)
- Shows: Chat interface + live preview panel
- Appearance: Clean, welcoming, focused

#### Step 2: Conversational AI Chat
Claude API (Opus 4) asks guided questions across multiple turns:

```
Turn 1:
Assistant: "Hello! I'm here to help you create a beautiful timeline 
for your health journey. What condition or procedure are you documenting? 
What dates does it span?"

User: "Chiari malformation surgery, February 26 - March 5, 2026. 
Suboccipital craniectomy with C1 laminectomy and duraplasty."

Turn 2:
Assistant: "Thank you for sharing. That's a significant procedure. 
What were the main milestones? (Example: pre-op evaluation, surgery day, 
post-op week, recovery phases)"

User: "Pre-op on Feb 20-25, surgery Feb 26, hospital stay Feb 26-Mar 1, 
home recovery Mar 1-5"

Turn 3:
Assistant: "Beautiful. Any faith or spiritual moments during this journey 
you'd like to include?"

User: "Yes, a lot of prayer and spiritual strength. My faith community 
was very supportive."

Turn 4:
Assistant: "That's powerful. Do you have photos or videos to include? 
You can upload them now or skip."

User: "I have a post-op walk video and some recovery photos."

Turn 5:
Assistant: "Perfect. Is this journey private (invite-only), semi-private 
(login required), or public (shareable with everyone)?"

User: "Public. I want others facing Chiari to see my story."
```

#### Step 3: AI Generates Structure
Based on conversation, Claude generates:

```json
{
  "title": "Chiari Malformation Surgery Recovery",
  "condition": "Chiari Malformation (15mm herniation)",
  "procedure_type": "Suboccipital Craniectomy + C1 Laminectomy + Duraplasty",
  "start_date": "2026-02-20",
  "end_date": "2026-03-05",
  "summary": "A 25-year-old's journey through diagnosis, surgery, and recovery 
for a significant brain condition. From pre-op anxieties to post-op triumphs.",
  
  "stages": [
    {
      "name": "Pre-Operative Evaluation",
      "description": "Medical testing, consultation, preparation",
      "color": "#5b8fa8",
      "dates": "Feb 20-25"
    },
    {
      "name": "Surgery Day",
      "description": "Suboccipital craniectomy procedure",
      "color": "#5b8fa8",
      "dates": "Feb 26"
    },
    {
      "name": "Hospital Stay",
      "description": "Post-operative monitoring and recovery",
      "color": "#5b8fa8",
      "dates": "Feb 26 - Mar 1"
    },
    {
      "name": "Early Home Recovery",
      "description": "Initial recovery at home, restricted activity",
      "color": "#a05c5c",
      "dates": "Mar 1-5"
    },
    {
      "name": "Family Support",
      "description": "Daily care from family, emotional support",
      "color": "#c9a84c",
      "dates": "Throughout"
    }
  ],
  
  "timeline_entries": [
    {
      "date": "2026-02-20",
      "type": "clinical",
      "title": "Final Pre-Op Consultation",
      "content": "Met with neurosurgery team. Last imaging before surgery. Discussed risks and recovery timeline.",
      "media": []
    },
    {
      "date": "2026-02-26",
      "type": "clinical",
      "title": "Surgery Day",
      "content": "Underwent suboccipital craniectomy with C1 laminectomy and duraplasty. Surgery was successful. Procedure took 4 hours.",
      "media": []
    },
    {
      "date": "2026-02-27",
      "type": "faith",
      "title": "Faith and Gratitude",
      "content": "Woke up after surgery. Prayers answered. Grateful for medical team and spiritual community.",
      "media": []
    },
    {
      "date": "2026-03-01",
      "type": "family",
      "title": "Going Home",
      "content": "Discharged from hospital. Family support amazing. Can't wait to sleep in my own bed.",
      "media": ["discharge.webp"]
    },
    {
      "date": "2026-03-04",
      "type": "clinical",
      "title": "First Walk",
      "content": "Took first post-op walk around the house. Small victory, huge milestone.",
      "media": ["post-surgery-walk.mov"]
    }
  ],
  
  "color_scheme": {
    "clinical": "#5b8fa8",
    "faith": "#a05c5c",
    "family": "#c9a84c",
    "accent": "#181b1e"
  },
  
  "privacy": "public",
  "diagrams": [
    {
      "title": "What is a Chiari Malformation?",
      "description": "Brain tissue extends into spinal canal. Surgery relieves pressure.",
      "svg": "<svg>...</svg>"
    }
  ]
}
```

#### Step 4: Preview & Edit
User sees real-time preview panel updating:
- Journey title and dates
- Color-coded stages
- Sample timeline entries
- Can add/edit entries manually
- Can upload photos and videos
- Can adjust privacy level

#### Step 5: Generate & Publish
System creates:
- Unique URL: `/health-journey/[user-id]/[journey-slug]`
  - Example: `/health-journey/joe-young/chiari-surgery-2026`
- Full HTML page (like Surgery Day)
- Share link: `/health-journey/[slug]?share_token=[token]`
- Embed code: `<iframe src="..." />`
- User dashboard entry

---

## PART 3: DATABASE DESIGN

### New Tables

```sql
-- health_journeys: Main journey record
CREATE TABLE health_journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- URL & slug
    slug VARCHAR(255) NOT NULL UNIQUE,
    
    -- Journey metadata
    title VARCHAR(255) NOT NULL,
    condition VARCHAR(255),
    procedure_type VARCHAR(255),
    description TEXT,
    summary TEXT,
    
    -- Timeline
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('planning', 'active', 'completed') DEFAULT 'active',
    
    -- AI-generated content (JSON)
    stages JSONB,  -- [{name, description, color, dates}, ...]
    timeline_entries JSONB,  -- [{date, type, title, content, media}, ...]
    color_scheme JSONB,  -- {clinical, faith, family, accent}
    diagrams JSONB,  -- [{title, description, svg}, ...]
    
    -- Media
    gallery_photos JSONB,  -- [{url, caption, date, alt_text}, ...]
    videos JSONB,  -- [{url, title, thumbnail, duration}, ...]
    
    -- Privacy & sharing
    privacy ENUM('private', 'semi-private', 'public') DEFAULT 'semi-private',
    share_token VARCHAR(255) UNIQUE,  -- For private share links
    embed_code TEXT,  -- Generated iframe code
    
    -- Publishing
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    views INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_slug (slug),
    INDEX idx_privacy (privacy),
    INDEX idx_published (is_published)
);

-- journey_entries: Individual timeline entries (optional normalized structure)
CREATE TABLE journey_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES health_journeys(id) ON DELETE CASCADE,
    
    entry_date DATE NOT NULL,
    entry_type ENUM('clinical', 'faith', 'family', 'milestone') NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    
    -- Media URLs (stored as JSON array or foreign key)
    media_urls JSONB,
    
    -- Metadata
    tags JSONB,  -- ["recovery", "hospital", ...]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_journey_id (journey_id),
    INDEX idx_entry_date (entry_date)
);

-- journey_comments: Community support comments
CREATE TABLE journey_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES health_journeys(id) ON DELETE CASCADE,
    entry_id UUID REFERENCES journey_entries(id) ON DELETE SET NULL,
    
    -- Commenter info
    commenter_name VARCHAR(255) NOT NULL,
    commenter_email VARCHAR(255),
    
    -- Comment
    comment_text TEXT NOT NULL,
    reaction_type ENUM('heart', 'hug', 'encouragement', 'celebration'),
    
    -- Moderation
    is_approved BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_journey_id (journey_id),
    INDEX idx_entry_id (entry_id),
    INDEX idx_is_approved (is_approved)
);

-- journey_sessions: Track multi-turn AI conversations
CREATE TABLE journey_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_token VARCHAR(255) UNIQUE,
    
    -- Conversation history
    conversation_history JSONB,  -- [{role, content}, ...]
    journey_structure JSONB,  -- Generated structure so far
    
    -- Status
    is_complete BOOLEAN DEFAULT FALSE,
    journey_id UUID REFERENCES health_journeys(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- Auto-expire old sessions
    
    INDEX idx_session_token (session_token),
    INDEX idx_user_id (user_id)
);

-- journey_media: Uploaded photos and videos
CREATE TABLE journey_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES health_journeys(id) ON DELETE CASCADE,
    
    media_type ENUM('image', 'video') NOT NULL,
    file_path VARCHAR(255) NOT NULL,  -- S3 path
    original_filename VARCHAR(255),
    
    -- Metadata
    caption TEXT,
    alt_text VARCHAR(255),
    upload_date DATE,
    file_size_bytes INTEGER,
    
    -- AI-generated
    auto_caption TEXT,  -- Generated by Claude vision
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_journey_id (journey_id)
);
```

---

## PART 4: API ENDPOINTS

### Chat & Journey Creation

```
POST /api/journey/builder/start
  Returns: {session_id, initial_message}
  No auth required (anonymous session)

POST /api/journey/builder/chat
  Input: {session_id, message}
  Output: {response, journey_structure, needs_more_info, current_stage}
  - Multi-turn conversation
  - Real-time preview updates
  - Extracts JSON when conversation complete

GET /api/journey/builder/session/{session_id}
  Returns: {conversation_history, journey_structure}
```

### Journey Management

```
POST /api/journey/create
  Input: {title, condition, procedure_type, start_date, end_date, 
           stages, timeline_entries, color_scheme, privacy}
  Output: {journey_id, slug, share_url, embed_code}
  Auth required (creates under current user)

GET /api/journey/{id}
  Returns: full journey data
  Auth: owner only OR public/semi-private with login OR private with share_token

PUT /api/journey/{id}
  Input: {title, description, stages, timeline_entries, color_scheme, privacy}
  Output: updated journey
  Auth: owner only

DELETE /api/journey/{id}
  Auth: owner only
  Deletes journey and all related data

GET /api/journey/{id}/share-link
  Returns: {share_url, share_token, embed_code}
  Auth: owner only
```

### Timeline Entries

```
POST /api/journey/{journey_id}/entry
  Input: {date, type, title, content, media_urls, tags}
  Output: {entry_id}
  Auth: owner or co-author

PUT /api/journey/{journey_id}/entry/{entry_id}
  Input: {date, type, title, content, media_urls, tags}
  Output: updated entry
  Auth: owner or co-author

DELETE /api/journey/{journey_id}/entry/{entry_id}
  Auth: owner or co-author

GET /api/journey/{journey_id}/entries
  Returns: [{entry}, ...]
  Pagination: ?limit=20&offset=0
```

### Media Management

```
POST /api/journey/{journey_id}/media/upload
  Input: FormData {file, caption, alt_text, type}
  Output: {media_id, url, thumb_url}
  Auth: owner or co-author
  - Max 100 MB per file
  - Supports: jpg, png, webp, mp4, mov, webm
  - Auto-generates thumbnail for images
  - Auto-generates caption via Claude vision

GET /api/journey/{journey_id}/media
  Returns: [{media}, ...]
  Auth: based on journey privacy

DELETE /api/journey/{journey_id}/media/{media_id}
  Auth: owner only
```

### Comments & Reactions

```
POST /api/journey/{journey_id}/comment
  Input: {name, email, comment, reaction_type}
  Output: {comment_id}
  Auth: not required (public comments)
  - Requires moderation approval before display
  - Email notification to journey owner

GET /api/journey/{journey_id}/comments
  Returns: [{comment}, ...] (approved only)
  Pagination: ?limit=50&offset=0

PUT /api/journey/{journey_id}/comment/{comment_id}/approve
  Auth: owner only

DELETE /api/journey/{journey_id}/comment/{comment_id}
  Auth: owner only
```

### Analytics & Discovery

```
GET /api/journey/search
  Query: ?q=chiari&condition=neurology&date_range=2026
  Returns: [{journey}, ...]
  - Full-text search on title, condition, summary
  - Filter by condition, date range
  - Sort by date, popularity, relevance
  - Public journeys only

GET /api/journey/trending
  Returns: [{journey}, ...] (by views last 30 days)
  Public journeys only

GET /api/journey/by-condition/{condition}
  Returns: [{journey}, ...] (all public journeys with this condition)

POST /api/journey/{id}/view
  Input: {}
  Effect: increments view counter
  Auth: not required
```

### Sharing

```
POST /api/journey/{journey_id}/share
  Input: {emails, message}
  Output: {share_url, sent_to}
  Auth: owner only
  - Sends email notifications
  - Creates temporary share token
  - Includes custom message

GET /api/journey/{journey_id}/share-status
  Returns: {privacy, share_url, share_token, who_has_access}
  Auth: owner only
```

---

## PART 5: BACKEND IMPLEMENTATION

### Service: Journey Generator

```python
# app/services/journey_generator.py

from anthropic import Anthropic
import json
import re
from typing import Optional, Dict, List

class JourneyGenerator:
    """Multi-turn conversation for generating health journeys using Claude."""
    
    def __init__(self):
        self.client = Anthropic()
    
    def get_system_prompt(self) -> str:
        """System prompt for journey creation conversation."""
        return """You are a compassionate healthcare storyteller helping users 
document their medical journeys. Your role is to:

1. Ask clarifying questions about their condition, timeline, and milestones
2. Understand the emotional and spiritual dimensions of their journey
3. Help them structure their story into logical stages
4. Suggest appropriate colors, visuals, and entry types
5. Generate JSON timeline structure when information is complete

Guidelines:
- Be warm, empathetic, and professional
- Validate dates and timelines for accuracy
- Encourage inclusion of faith/family elements if relevant
- Respect privacy preferences
- When you have enough information, output JSON in ```json``` block

Required information before generating:
- Procedure/condition name
- Timeline (start and end dates, or start + expected duration)
- Major milestones or stages
- Patient comfort with sharing publicly
- Optional: photos, videos, faith/family moments"""
    
    def process_user_input(self, session_id: str, user_message: str, 
                          conversation_history: List[Dict]) -> Dict:
        """Process user input and generate journey structure."""
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get Claude response
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            system=self.get_system_prompt(),
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Try to extract JSON structure
        journey_structure = self._extract_journey_json(assistant_message)
        
        return {
            "response": assistant_message,
            "journey_structure": journey_structure,
            "conversation_history": conversation_history,
            "needs_more_info": journey_structure is None,
            "message_count": len(conversation_history)
        }
    
    def _extract_journey_json(self, response: str) -> Optional[Dict]:
        """Extract journey JSON if conversation indicates completion."""
        # Look for JSON in ```json``` block
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None
        return None
    
    def generate_svg_diagram(self, procedure_description: str) -> str:
        """Generate SVG medical diagram using Claude."""
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Generate an SVG medical diagram for this procedure:

{procedure_description}

Requirements:
- Simple, clean, professional style (no gradients)
- Clearly labeled anatomical parts
- Step-by-step if applicable (e.g., surgical stages)
- Max 600px width, viewBox="0 0 600 400"
- Color palette: 
  - #5b8fa8 (clinical blue)
  - #181b1e (dark background)
  - #e8e3d8 (light text)
  - #c9a84c (accent gold)
- Use serif fonts (Georgia or similar for readability)
- Include title as <text> element
- Accessibility: include descriptions in comments

Output ONLY the SVG code, no markdown, no explanations, no backticks."""
            }]
        )
        
        return response.content[0].text
    
    def generate_timeline_entries(self, journey_info: Dict) -> List[Dict]:
        """Generate suggested timeline entries based on journey info."""
        
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""Create 7-12 timeline entry suggestions for this health journey:

Title: {journey_info.get('title')}
Condition: {journey_info.get('condition')}
Procedure: {journey_info.get('procedure_type')}
Dates: {journey_info.get('start_date')} to {journey_info.get('end_date', 'ongoing')}
Milestones: {', '.join(journey_info.get('milestones', []))}

Generate realistic, compassionate entries covering:
- Pre-operative phase (preparations, emotions)
- Surgery day (facts + feelings)
- Post-operative recovery (clinical + personal)
- Return to normalcy (milestones, reflections)

For each entry, provide:
- Date (YYYY-MM-DD)
- Type: 'clinical', 'faith', 'family', or 'milestone'
- Title (short, compelling)
- Content (2-3 sentences, first person)

Format as JSON array. Output ONLY JSON, no markdown.

[
  {{
    "date": "2026-02-20",
    "type": "clinical",
    "title": "Pre-Op Consultation",
    "content": "Met with my neurosurgery team today..."
  }},
  ...
]"""
            }]
        )
        
        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            return []
    
    def generate_color_scheme(self, condition: str, patient_preferences: str = "") -> Dict:
        """Generate appropriate color scheme based on condition."""
        
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Generate a color scheme for a health journey timeline:

Condition: {condition}
Patient preferences: {patient_preferences or "None specified"}

Choose colors that:
- Reflect the medical condition's visual identity (if applicable)
- Inspire hope and healing
- Are accessible (AA contrast ratio)
- Work for clinical, faith, and family entry types

Return JSON with hex colors:
{{
  "clinical": "#5b8fa8",
  "faith": "#a05c5c", 
  "family": "#c9a84c",
  "accent": "#181b1e",
  "background": "#e8e3d8"
}}

Output ONLY JSON."""
            }]
        )
        
        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            # Fallback default colors
            return {
                "clinical": "#5b8fa8",
                "faith": "#a05c5c",
                "family": "#c9a84c",
                "accent": "#181b1e",
                "background": "#e8e3d8"
            }


# Flask routes using this service
# app/routes/journey.py

from flask import Blueprint, request, jsonify, render_template, session
from app.services.journey_generator import JourneyGenerator
from app.models import HealthJourney, JourneySession
from app.auth import login_required, get_current_user
from app import db
import uuid

journey_bp = Blueprint('journey', __name__, url_prefix='/journey')
generator = JourneyGenerator()


@journey_bp.route('/builder', methods=['GET'])
def builder():
    """Chat interface for creating journey."""
    return render_template('surgery-day-builder/chat.html')


@journey_bp.route('/api/builder/start', methods=['POST'])
def start_builder():
    """Start new journey builder session."""
    session_id = str(uuid.uuid4())
    
    journey_session = JourneySession(
        id=session_id,
        user_id=get_current_user().id if get_current_user() else None,
        session_token=str(uuid.uuid4()),
        conversation_history=[],
        expires_at=datetime.now() + timedelta(hours=24)
    )
    db.session.add(journey_session)
    db.session.commit()
    
    return jsonify({
        "session_id": session_id,
        "initial_message": "Hello! I'm here to help you create a beautiful timeline for your health journey. "
                          "Let's start: What condition or procedure are you documenting? What dates does it span?"
    })


@journey_bp.route('/api/builder/chat', methods=['POST'])
def chat():
    """Process user message in journey builder."""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    # Get or create session
    journey_session = JourneySession.query.filter_by(id=session_id).first_or_404()
    
    # Process through Claude
    result = generator.process_user_input(
        session_id=session_id,
        user_message=user_message,
        conversation_history=journey_session.conversation_history or []
    )
    
    # Update session with conversation history
    journey_session.conversation_history = result['conversation_history']
    journey_session.journey_structure = result['journey_structure']
    db.session.commit()
    
    return jsonify({
        "response": result['response'],
        "journey_structure": result['journey_structure'],
        "needs_more_info": result['needs_more_info'],
        "message_count": result['message_count']
    })


@journey_bp.route('/api/builder/generate', methods=['POST'])
def generate_journey():
    """Finalize and create journey from session."""
    data = request.json
    session_id = data.get('session_id')
    
    journey_session = JourneySession.query.filter_by(id=session_id).first_or_404()
    journey_structure = journey_session.journey_structure
    
    if not journey_structure:
        return jsonify({"error": "Journey structure not yet generated"}), 400
    
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Authentication required"}), 401
    
    # Create slug from title
    slug = journey_structure['title'].lower().replace(' ', '-')[:50]
    
    # Create health journey record
    journey = HealthJourney(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        slug=f"{slug}-{uuid.uuid4().hex[:6]}",  # Make unique
        title=journey_structure['title'],
        condition=journey_structure.get('condition'),
        procedure_type=journey_structure.get('procedure_type'),
        summary=journey_structure.get('summary'),
        start_date=journey_structure.get('start_date'),
        end_date=journey_structure.get('end_date'),
        stages=journey_structure.get('stages'),
        timeline_entries=journey_structure.get('timeline_entries'),
        color_scheme=journey_structure.get('color_scheme'),
        diagrams=journey_structure.get('diagrams'),
        privacy=journey_structure.get('privacy', 'semi-private'),
        is_published=True,
        published_at=datetime.now()
    )
    
    db.session.add(journey)
    db.session.commit()
    
    # Link session to journey
    journey_session.journey_id = journey.id
    db.session.commit()
    
    return jsonify({
        "journey_id": journey.id,
        "slug": journey.slug,
        "url": f"/health-journey/{journey.slug}",
        "share_url": f"/health-journey/{journey.slug}?share_token={journey.share_token}",
        "embed_code": f'<iframe src="/health-journey/{journey.slug}" width="100%" height="1000" frameborder="0"></iframe>'
    })
```

---

## PART 6: FRONTEND INTERFACE

### Chat Builder Page

```html
<!-- templates/surgery-day-builder/chat.html -->

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Create Your Health Journey Timeline</title>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Crimson+Pro:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --black: #181b1e;
      --white: #e8e3d8;
      --gold: #c9a84c;
      --clinical: #5b8fa8;
      --faith: #a05c5c;
      --family: #c9a84c;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Crimson Pro', serif;
      background: var(--white);
      color: var(--black);
      line-height: 1.6;
    }
    
    .container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
      min-height: 100vh;
    }
    
    @media (max-width: 768px) {
      .container {
        grid-template-columns: 1fr;
      }
    }
    
    /* Chat Panel */
    .chat-panel {
      display: flex;
      flex-direction: column;
      border: 2px solid var(--black);
      border-radius: 8px;
      overflow: hidden;
      background: white;
    }
    
    .chat-header {
      background: var(--black);
      color: var(--white);
      padding: 1.5rem;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1.5rem;
      letter-spacing: 2px;
    }
    
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      max-height: 600px;
    }
    
    .message {
      margin-bottom: 1.5rem;
      animation: slideIn 0.3s ease-in;
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .message.user {
      text-align: right;
    }
    
    .message.assistant {
      text-align: left;
    }
    
    .message p {
      padding: 1rem;
      border-radius: 8px;
      max-width: 80%;
      display: inline-block;
      word-wrap: break-word;
    }
    
    .message.user p {
      background: var(--gold);
      color: var(--black);
    }
    
    .message.assistant p {
      background: var(--black);
      color: var(--white);
    }
    
    .chat-form {
      padding: 1.5rem;
      border-top: 1px solid #ddd;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    textarea {
      font-family: 'Crimson Pro', serif;
      font-size: 1rem;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      resize: vertical;
      min-height: 80px;
    }
    
    button {
      background: var(--black);
      color: var(--white);
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1rem;
      letter-spacing: 1px;
      cursor: pointer;
      transition: background 0.3s;
    }
    
    button:hover {
      background: var(--gold);
      color: var(--black);
    }
    
    /* Preview Panel */
    .preview-panel {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    
    .preview-section {
      border: 2px solid var(--black);
      padding: 1.5rem;
      border-radius: 8px;
    }
    
    .preview-section h3 {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1.2rem;
      letter-spacing: 1px;
      margin-bottom: 1rem;
      border-bottom: 2px solid var(--gold);
      padding-bottom: 0.5rem;
    }
    
    .stages {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .stage {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.75rem;
      background: #f5f5f5;
      border-radius: 4px;
    }
    
    .stage-dot {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    
    .metadata {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      font-size: 0.9rem;
    }
    
    .metadata-item {
      display: flex;
      justify-content: space-between;
    }
    
    .metadata-label {
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Left: Chat Interface -->
    <div class="chat-panel">
      <div class="chat-header">Journey Builder</div>
      <div class="messages" id="messages"></div>
      <form class="chat-form" id="chat-form">
        <textarea id="user-input" placeholder="Share your health journey..."></textarea>
        <button type="submit">Send</button>
      </form>
    </div>
    
    <!-- Right: Live Preview -->
    <div class="preview-panel">
      <div class="preview-section">
        <h3>Your Journey</h3>
        <div id="preview-content">
          <p style="color: #999;">Information will appear here as you chat...</p>
        </div>
      </div>
      
      <div class="preview-section">
        <h3>Stages</h3>
        <div class="stages" id="stages-preview">
          <p style="color: #999;">Waiting for journey details...</p>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    let sessionId = null;
    
    // Initialize
    async function init() {
      const response = await fetch('/journey/api/builder/start', {method: 'POST'});
      const data = await response.json();
      sessionId = data.session_id;
      addMessage('assistant', data.initial_message);
    }
    
    // Handle form submission
    document.getElementById('chat-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const input = document.getElementById('user-input');
      const message = input.value.trim();
      
      if (!message) return;
      
      addMessage('user', message);
      input.value = '';
      
      // Show typing indicator
      const typingEl = document.createElement('div');
      typingEl.className = 'message assistant';
      typingEl.innerHTML = '<p style="color: #999;">Thinking...</p>';
      document.getElementById('messages').appendChild(typingEl);
      
      try {
        const response = await fetch('/journey/api/builder/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({session_id: sessionId, message})
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        typingEl.remove();
        
        addMessage('assistant', data.response);
        
        if (data.journey_structure) {
          updatePreview(data.journey_structure);
        }
      } catch (error) {
        typingEl.remove();
        addMessage('assistant', 'Sorry, there was an error. Please try again.');
        console.error(error);
      }
    });
    
    function addMessage(role, content) {
      const messagesDiv = document.getElementById('messages');
      const messageEl = document.createElement('div');
      messageEl.className = `message ${role}`;
      messageEl.innerHTML = `<p>${content}</p>`;
      messagesDiv.appendChild(messageEl);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    function updatePreview(structure) {
      // Update metadata
      const metadata = `
        <div class="metadata">
          <div class="metadata-item">
            <span class="metadata-label">Title:</span>
            <span>${structure.title}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Condition:</span>
            <span>${structure.condition || 'Not specified'}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Dates:</span>
            <span>${structure.start_date} to ${structure.end_date || 'ongoing'}</span>
          </div>
        </div>
      `;
      document.getElementById('preview-content').innerHTML = metadata;
      
      // Update stages
      if (structure.stages && structure.stages.length > 0) {
        const stagesHtml = structure.stages.map(stage => `
          <div class="stage">
            <div class="stage-dot" style="background: ${stage.color}"></div>
            <div>
              <strong>${stage.name}</strong>
              <p style="font-size: 0.85rem; color: #666;">${stage.description}</p>
            </div>
          </div>
        `).join('');
        document.getElementById('stages-preview').innerHTML = stagesHtml;
      }
    }
    
    // Start when page loads
    init();
  </script>
</body>
</html>
```

---

## PART 7: GENERATED PAGE TEMPLATE

The generated page looks like Surgery Day:

```html
<!-- templates/surgery-day-builder/journey-page.html -->
<!-- Dynamically rendered from journey data -->

Similar structure to /surgery-day.html:
- Fixed navigation (hamburger menu)
- Page header (title, metadata, legend)
- Progress board (color-coded stages)
- Timeline (chronological entries, color-tagged)
- SVG diagrams (procedure explanation)
- Photo gallery (responsive grid)
- Comments section (Firebase or DB)
- Share/embed buttons
```

---

## PART 8: INTEGRATION WITH PECK'S MISSION

### How It Fits
1. **User Type:** Healthcare storytellers (patients, caregivers, clinicians)
2. **Core Value:** Democratizes beautiful healthcare timeline creation (no HTML needed)
3. **Content:** Feeds into blog/resources section if made public
4. **Community:** Comments + reactions build community like CaringBridge
5. **Educational:** Timelines become case studies and resources

### URL Structure
- `/surgery-day-builder` — Public chat interface
- `/health-journey/{slug}` — Generated public/shared timeline
- `/dashboard/journeys` — User's list of journeys (authenticated)
- `/resources/journeys` — Public gallery of all journeys (filterable by condition)

### Privacy Model (Like CaringBridge)
- **Public:** Shared widely, searchable, indexed
- **Semi-Private:** Login required to view
- **Private:** Share token required (invite-only)

---

## PART 9: IMPLEMENTATION CHECKLIST

### Phase 1: Database & Models (Week 1-2)
- ☐ Create `health_journeys` table
- ☐ Create `journey_entries` table
- ☐ Create `journey_comments` table
- ☐ Create `journey_sessions` table
- ☐ Create `journey_media` table
- ☐ Add database migrations
- ☐ Create SQLAlchemy models

### Phase 2: Backend Services (Week 2-3)
- ☐ Build `JourneyGenerator` service (Claude integration)
- ☐ Implement multi-turn conversation logic
- ☐ SVG diagram generation
- ☐ Timeline entry suggestion
- ☐ Color scheme generation
- ☐ Session management

### Phase 3: API Endpoints (Week 3-4)
- ☐ `/api/builder/start` — Initialize session
- ☐ `/api/builder/chat` — Process messages
- ☐ `/api/builder/generate` — Create journey
- ☐ `/api/journey/create` — Manual creation
- ☐ `/api/journey/{id}` — CRUD operations
- ☐ `/api/journey/{id}/entry` — Timeline entries
- ☐ `/api/journey/{id}/media/upload` — Media handling
- ☐ `/api/journey/{id}/comment` — Comments

### Phase 4: Frontend (Week 4-5)
- ☐ Chat builder interface (`/surgery-day-builder`)
- ☐ Real-time preview panel
- ☐ Message handling & rendering
- ☐ Form validation
- ☐ Responsive design (mobile-first)

### Phase 5: Page Generation (Week 5-6)
- ☐ Journey page template
- ☐ Dynamic CSS (color schemes)
- ☐ Progress board rendering
- ☐ Timeline rendering
- ☐ Gallery grid layout
- ☐ Comments section
- ☐ Share/embed modals

### Phase 6: Testing & Refinement (Week 6-7)
- ☐ User testing (real health journeys)
- ☐ Claude prompt refinement
- ☐ Edge case handling
- ☐ Performance optimization
- ☐ Accessibility audit
- ☐ Mobile responsiveness

### Phase 7: Launch (Week 7-8)
- ☐ Documentation
- ☐ Email announcement
- ☐ Blog post tutorial
- ☐ Social media campaign
- ☐ Monitor usage & feedback

---

## Key Features Summary

| Feature | Description | Owner | Privacy |
|---------|-------------|-------|---------|
| Multi-turn Chat | Claude conversation to gather journey details | All users | Session-based |
| Auto-Structure | AI generates stages, timeline, colors | All users | Real-time preview |
| SVG Diagrams | Auto-generated medical visualizations | All users | Part of journey |
| Timeline Entries | 7-12 suggested entries per journey | All users | User-editable |
| Media Upload | Photos, videos with AI captions | Authenticated | Configurable |
| Comments | Community support messages | All users | Author-moderated |
| Sharing | Public, semi-private, or private | Journey owner | Privacy-controlled |
| Embeddable | Iframe code for blogs/websites | Public journeys | External |
| Search | Full-text search by condition, date | All users | Public only |

---

## Success Metrics

1. **Adoption:** # of journeys created per week
2. **Quality:** Average completion rate (% conversations → published journeys)
3. **Community:** # of comments/reactions per journey
4. **Content:** # of public journeys feeding resources section
5. **User Satisfaction:** NPS, testimonials, repeat usage
6. **Traffic:** Referral traffic from journey pages to homepage

---

## Next Steps

1. **Design & estimate:** Frontend design review
2. **DB migration:** Set up new tables
3. **Claude integration:** Test prompt engineering
4. **Prototype:** Build MVP (chat + preview)
5. **Test:** Run with 5-10 real users
6. **Iterate:** Refine based on feedback
7. **Launch:** Beta release to Peck's Mission community

---

This is everything needed to build an AI-powered Surgery Day generator for Peck's Mission.
