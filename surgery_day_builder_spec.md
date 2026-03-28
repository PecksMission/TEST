# Surgery Day Builder — AI-Powered Timeline Generator

## Overview
A system that lets users create personalized "Surgery Day" timeline pages through conversational AI prompts. Users describe their health journey, and AI generates an interactive timeline similar to the Surgery Day example.

## Architecture

### User Flow
1. User visits `/surgery-day-builder` (new page)
2. AI chat interface asks guided questions:
   - What procedure/condition?
   - Timeline (start date, expected duration)
   - Key milestones (pre-op, surgery day, recovery phases)
   - Photo gallery? Video? Captions?
   - Is this private or sharable?
3. User provides details via chat
4. AI generates:
   - Surgical stages/phases
   - Timeline entries
   - Color scheme (based on condition/type)
   - SVG diagrams (auto-generated)
5. System creates unique page: `/health-journey/[user-id]/[journey-slug]`
6. User can edit, share, or embed timeline

### Database Schema

```sql
-- New table: health_journeys
CREATE TABLE health_journeys (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    slug VARCHAR(255) UNIQUE,
    title VARCHAR(255),
    condition VARCHAR(255),
    procedure_type VARCHAR(255),
    start_date DATE,
    end_date DATE (optional),
    status ENUM('planning', 'active', 'completed'),
    
    -- AI-generated content
    summary TEXT,
    stages JSON (array of {name, description, color}),
    timeline_entries JSON (array of {date, type, content, media}),
    color_scheme JSON {clinical, faith, family, accent},
    
    -- Privacy & sharing
    privacy ENUM('private', 'semi-private', 'public'),
    share_token VARCHAR(255) (for shareable link),
    embed_code TEXT,
    
    -- Media
    gallery_photos JSON (array of {url, caption, date}),
    videos JSON (array of {url, title, thumbnail}),
    diagrams JSON (array of {svg, description}),
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_published BOOLEAN
);

-- New table: journey_entries (individual timeline posts)
CREATE TABLE journey_entries (
    id UUID PRIMARY KEY,
    journey_id UUID FOREIGN KEY,
    date DATE,
    type ENUM('clinical', 'faith', 'family', 'milestone'),
    title VARCHAR(255),
    content TEXT (rich text / markdown),
    media_urls JSON,
    tags JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- New table: journey_comments (Firebase replacement for smaller deployments)
CREATE TABLE journey_comments (
    id UUID PRIMARY KEY,
    journey_id UUID FOREIGN KEY,
    entry_id UUID FOREIGN KEY (optional),
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    comment TEXT,
    reaction_type ENUM('heart', 'hug', 'encouragement', 'celebration'),
    created_at TIMESTAMP
);
```

### API Endpoints

```
POST /api/journey/create
  Input: {condition, procedure, start_date, description, photos[], videos[]}
  Output: {journey_id, share_url, embed_code, edit_token}

POST /api/journey/{id}/generate-timeline
  Input: {ai_prompt, photos, video, additional_details}
  Output: {stages, entries, color_scheme, diagrams}

GET /api/journey/{slug}
  Output: full journey data (public/semi-private/private based on share_token)

PUT /api/journey/{id}/update
  Input: {title, entries, stages, privacy, color_scheme}
  Output: updated journey

POST /api/journey/{id}/entry/add
  Input: {date, type, title, content, media}
  Output: new entry

GET /health-journey/{slug}
  (or /health-journey/{user-id}/{slug})
  Renders generated HTML page (like Surgery Day)

GET /health-journey/{slug}/embed
  Returns embeddable iframe code

POST /api/journey/{id}/share
  Input: {email_list}
  Output: sends share notifications
```

### AI Prompt Examples

**Initial Prompt:**
```
"Tell me about your health journey. What procedure or condition are you documenting? 
What dates does it span? What are the major milestones? 
(Example: 'Chiari malformation surgery, February 26 - March 5, 2026. Surgery day Feb 26, post-op week, recovery milestones.')"
```

**Follow-up Prompts:**
- "Any faith or spiritual moments you want to include?"
- "Family support moments or milestones?"
- "Do you have photos or videos to include?"
- "Any insights or lessons learned?"

### Claude Integration

```python
# app/services/journey_generator.py

from anthropic import Anthropic

class JourneyGenerator:
    def __init__(self):
        self.client = Anthropic()
        self.conversation_history = []
    
    def start_journey_chat(self):
        """Initialize multi-turn conversation for journey creation"""
        system_prompt = """You are a compassionate healthcare storyteller helping users document their medical journey.
Your role is to:
1. Ask clarifying questions about their condition, timeline, and milestones
2. Help them structure their story into stages
3. Suggest color schemes and visual elements
4. Generate entry suggestions for each stage
5. Create SVG diagrams to explain their procedure

You gather information conversationally, then output JSON with journey structure.
Always validate dates, ensure privacy preferences are respected, offer to include faith/family elements.
"""
        return system_prompt
    
    def process_user_input(self, user_message: str) -> dict:
        """Process user input and generate journey structure"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            system=self.start_journey_chat(),
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Try to parse JSON from response if complete
        journey_structure = self._extract_journey_json(assistant_message)
        
        return {
            "response": assistant_message,
            "journey_structure": journey_structure,
            "needs_more_info": journey_structure is None
        }
    
    def _extract_journey_json(self, response: str) -> dict:
        """Extract journey JSON if conversation is complete"""
        import json
        import re
        
        # Look for JSON block in response
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None
        return None
    
    def generate_svg_diagram(self, procedure_description: str) -> str:
        """Ask Claude to generate SVG for procedure explanation"""
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Generate an SVG medical diagram for this procedure:
{procedure_description}

Requirements:
- Simple, clean style (no gradients)
- Labeled parts
- Step-by-step (if applicable)
- Max 600px width
- Use colors: #5b8fa8 (clinical), #181b1e (background), #e8e3d8 (text)
- Include title and brief explanation below SVG

Output ONLY the SVG code, no markdown, no explanations."""
            }]
        )
        return response.content[0].text
    
    def generate_timeline_entries(self, journey_info: dict) -> list:
        """Generate suggested timeline entries"""
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""Create timeline entries for this health journey:
Title: {journey_info['title']}
Condition: {journey_info['condition']}
Dates: {journey_info['start_date']} to {journey_info.get('end_date', 'ongoing')}
Milestones: {', '.join(journey_info.get('milestones', []))}

Generate 5-10 suggested entries (date, type: clinical/faith/family, title, brief content).
Include pre-op, surgery day, post-op recovery.

Format as JSON array:
[
  {{"date": "2026-02-26", "type": "clinical", "title": "...", "content": "..."}},
  ...
]

Output ONLY JSON, no markdown."""
            }]
        )
        try:
            import json
            return json.loads(response.content[0].text)
        except:
            return []
```

### Frontend — AI Chat Interface

```html
<!-- /templates/surgery-day-builder/chat.html -->

<div class="journey-builder">
  <div class="chat-container">
    <div class="messages" id="messages">
      <div class="message assistant">
        <p>Hello! I'm here to help you create a beautiful timeline for your health journey.</p>
        <p>Let's start with the basics: What condition or procedure are you documenting?</p>
      </div>
    </div>
    
    <form id="chat-form" onsubmit="handleMessage(event)">
      <textarea id="user-input" placeholder="Tell me about your health journey..." rows="3"></textarea>
      <button type="submit">Send</button>
    </form>
  </div>
  
  <div class="preview-panel">
    <h3>Your Journey (Preview)</h3>
    <div id="preview" class="journey-preview">
      <!-- Updates as user inputs data -->
    </div>
  </div>
</div>

<script>
async function handleMessage(event) {
  event.preventDefault();
  
  const userInput = document.getElementById('user-input').value;
  document.getElementById('user-input').value = '';
  
  // Add user message to chat
  addMessage('user', userInput);
  
  // Send to backend
  const response = await fetch('/api/journey/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: userInput, session_id: getSessionId()})
  });
  
  const data = await response.json();
  addMessage('assistant', data.response);
  
  // Update preview if journey structure available
  if (data.journey_structure) {
    updatePreview(data.journey_structure);
  }
}

function addMessage(role, content) {
  const messagesDiv = document.getElementById('messages');
  const messageEl = document.createElement('div');
  messageEl.className = `message ${role}`;
  messageEl.innerHTML = `<p>${content}</p>`;
  messagesDiv.appendChild(messageEl);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function updatePreview(journeyStructure) {
  // Render preview of generated journey
  const preview = document.getElementById('preview');
  preview.innerHTML = `
    <h4>${journeyStructure.title}</h4>
    <p><strong>Dates:</strong> ${journeyStructure.start_date} to ${journeyStructure.end_date || 'ongoing'}</p>
    <h5>Stages:</h5>
    <div class="stages">
      ${journeyStructure.stages.map(s => `
        <div class="stage" style="border-color: ${s.color}">
          <span class="dot" style="background: ${s.color}"></span>
          ${s.name}
        </div>
      `).join('')}
    </div>
  `;
}
</script>
```

### Generated Page Template

```html
<!-- /templates/surgery-day-builder/journey-page.html -->
<!-- Dynamically rendered, similar to /surgery-day.html structure -->

<!DOCTYPE html>
<html>
<head>
  <title>{{ journey.title }} — {{ journey.condition }}</title>
  <style>
    :root {
      --clinical: {{ journey.color_scheme.clinical }};
      --faith: {{ journey.color_scheme.faith }};
      --family: {{ journey.color_scheme.family }};
      --gold: {{ journey.color_scheme.accent }};
    }
  </style>
</head>
<body>
  <!-- Navigation -->
  <nav class="fixed-nav">
    <!-- Hamburger menu, share button, edit button (if owner) -->
  </nav>
  
  <!-- Header -->
  <header>
    <h1>{{ journey.title }}</h1>
    <p class="metadata">{{ journey.condition }} • {{ journey.start_date }} to {{ journey.end_date }}</p>
    <div class="legend">
      <span class="legend-item clinical">Clinical Update</span>
      <span class="legend-item faith">Faith/Reflection</span>
      <span class="legend-item family">Family Moment</span>
    </div>
  </header>
  
  <!-- Progress Board -->
  <section class="progress-board">
    {% for stage in journey.stages %}
    <div class="stage" data-stage="{{ loop.index }}">
      <div class="dot" style="background: {{ stage.color }}"></div>
      <h3>{{ stage.name }}</h3>
      <p>{{ stage.description }}</p>
    </div>
    {% endfor %}
  </section>
  
  <!-- Timeline -->
  <section class="timeline">
    {% for entry in journey.timeline_entries %}
    <div class="entry type-{{ entry.type }}">
      <time>{{ entry.date }}</time>
      <h3>{{ entry.title }}</h3>
      <p>{{ entry.content }}</p>
      {% if entry.media %}
      <div class="media">
        {% for media in entry.media %}
          {% if media.type == 'image' %}
          <img src="{{ media.url }}" alt="{{ media.caption }}" />
          {% elif media.type == 'video' %}
          <video controls><source src="{{ media.url }}"></video>
          {% endif %}
        {% endfor %}
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </section>
  
  <!-- Diagrams Section -->
  {% if journey.diagrams %}
  <section class="diagrams">
    <h2>Procedure Overview</h2>
    {% for diagram in journey.diagrams %}
    <div class="diagram">
      {{ diagram.svg | safe }}
      <p>{{ diagram.description }}</p>
    </div>
    {% endfor %}
  </section>
  {% endif %}
  
  <!-- Gallery -->
  {% if journey.gallery_photos %}
  <section class="gallery">
    <h2>Journey Photos</h2>
    <div class="photo-grid">
      {% for photo in journey.gallery_photos %}
      <figure>
        <img src="{{ photo.url }}" alt="{{ photo.caption }}" />
        <figcaption>{{ photo.caption }}</figcaption>
      </figure>
      {% endfor %}
    </div>
  </section>
  {% endif %}
  
  <!-- Comments -->
  <section class="comments">
    <h2>Messages of Support</h2>
    <div id="comments-container"></div>
    <form id="comment-form" onsubmit="submitComment(event)">
      <input type="text" name="name" placeholder="Your name" />
      <textarea name="comment" placeholder="Share your support..."></textarea>
      <button type="submit">Post Comment</button>
    </form>
  </section>
</body>
</html>
```

### Routes

```python
# app/routes/journey.py

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.services.journey_generator import JourneyGenerator
from app.models import HealthJourney, JourneyEntry, JourneyComment
from app.auth import login_required, get_current_user
import uuid

journey_bp = Blueprint('journey', __name__, url_prefix='/journey')
generator = JourneyGenerator()

@journey_bp.route('/builder', methods=['GET'])
def builder():
    """Chat interface for creating journey"""
    return render_template('surgery-day-builder/chat.html')

@journey_bp.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and generate journey structure"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    # Retrieve or create session
    # session = JourneySession.query.filter_by(id=session_id).first()
    
    result = generator.process_user_input(user_message)
    
    return jsonify(result)

@journey_bp.route('/<slug>', methods=['GET'])
def view_journey(slug):
    """View published journey"""
    journey = HealthJourney.query.filter_by(slug=slug).first_or_404()
    
    # Check privacy
    share_token = request.args.get('share_token')
    if journey.privacy == 'private' and journey.share_token != share_token:
        if not is_owner(journey):
            return "Not accessible", 403
    
    # Render generated page
    return render_template('surgery-day-builder/journey-page.html', journey=journey)

@journey_bp.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journey(id):
    """Edit existing journey (owner only)"""
    journey = HealthJourney.query.get_or_404(id)
    current_user = get_current_user()
    
    if journey.user_id != current_user.id:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        journey.title = request.json.get('title')
        journey.timeline_entries = request.json.get('entries')
        journey.color_scheme = request.json.get('color_scheme')
        journey.is_published = request.json.get('is_published')
        db.session.commit()
        return jsonify({'success': True, 'url': url_for('journey.view_journey', slug=journey.slug)})
    
    return render_template('surgery-day-builder/edit.html', journey=journey)

@journey_bp.route('/<id>/share', methods=['POST'])
@login_required
def share_journey(id):
    """Generate share link and send notifications"""
    journey = HealthJourney.query.get_or_404(id)
    emails = request.json.get('emails', [])
    
    # Generate share token
    journey.share_token = str(uuid.uuid4())
    db.session.commit()
    
    share_url = url_for('journey.view_journey', slug=journey.slug, share_token=journey.share_token, _external=True)
    
    # Send emails
    for email in emails:
        # send_email(email, f"{journey.title} timeline", share_url)
        pass
    
    return jsonify({'share_url': share_url, 'embed_code': journey.embed_code})

@journey_bp.route('/<id>/embed', methods=['GET'])
def embed_journey(id):
    """Return embeddable iframe code"""
    journey = HealthJourney.query.get_or_404(id)
    iframe_url = url_for('journey.view_journey', slug=journey.slug, _external=True)
    embed_code = f'<iframe src="{iframe_url}" width="100%" height="1000" frameborder="0"></iframe>'
    return jsonify({'embed_code': embed_code})
```

## User Experience

### Step 1: Chat-Driven Creation
User describes health journey conversationally. AI asks clarifying questions, suggests structure.

### Step 2: Preview & Edit
User sees real-time preview of timeline stages, colors, and suggested entries. Can manually adjust.

### Step 3: Upload Media
User uploads photos, videos (optional). AI generates captions.

### Step 4: Generate Page
System creates unique URL: `/health-journey/[user-id]/[journey-slug]`
Page looks like Surgery Day — fixed nav, progress board, timeline, diagrams, gallery, comments.

### Step 5: Share
User can:
- Make public (Google-indexable, shareable)
- Make semi-private (login required)
- Make private with share token (invite-only)
- Get embed code for blogs/websites
- Email share notifications

## Privacy & Access

**Public:** Fully visible, Google-indexed, shareable.
**Semi-private:** Requires login to view.
**Private:** Share token required, not searchable.

Comments always require approval (author moderation).

## Integration with Peck's Mission

This fits perfectly:
- Users document their healthcare journey (like patients on CaringBridge)
- AI generates structure (Osler principle — treat the person, understand their story)
- Shareable timelines create community (family, friends, clinicians)
- Content becomes educational resource (feeds into /resources if made public)
- Feeds blog listing and user dashboard

## Tech Stack
- **Backend:** Flask, SQLAlchemy, Claude API (Opus)
- **Frontend:** Vanilla JS, CSS Grid/Flexbox (responsive)
- **Database:** PostgreSQL (journeys, entries, comments)
- **Media:** S3 (photos/videos), Redis (sessions)
- **CDN:** Firebase (optional, for comments if preferred)

