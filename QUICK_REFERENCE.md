# Surgery Day Builder - Quick Reference Guide

## What You're Getting

A complete, production-ready system for creating shareable healthcare journey timelines through conversational AI. Users chat with Claude, AI generates structure, system publishes a beautiful timeline page.

## Files Overview

### 1. **models_health_journey.py** (300 lines)
Database models for:
- `HealthJourney` - Main journey record
- `JourneyComment` - Comments with reactions

Copy to: `app/models/health_journey.py`

### 2. **services_journey_generator.py** (500 lines)
Claude API integration service:
- `JourneyGenerator` class
- Multi-turn conversation handling
- JSON extraction from responses
- SVG diagram generation
- Photo caption generation

Copy to: `app/services/journey_generator.py`

### 3. **routes_journey.py** (600 lines)
Flask routes and API endpoints:
- Chat interface (`GET /journey/builder`)
- Journey creation (`POST /api/journey`)
- View journey (`GET /health-journey/<slug>`)
- Comments & reactions
- Sharing & privacy

Copy to: `app/routes/journey.py`

### 4. **templates_journey_builder.html** (400 lines)
Chat interface with:
- Message history
- Real-time preview panel
- Responsive design
- JavaScript message handling

Copy to: `templates/journey/builder.html`

### 5. **templates_journey_view.html** (600 lines)
Published journey page with:
- Fixed navigation
- Progress board (stages)
- Timeline with entries
- Comments section
- Share modal

Copy to: `templates/journey/view.html`

### 6. **demo_journey.py** (300 lines)
Standalone test script:
- Test without Flask
- Interactive conversation
- Export to JSON
- No setup required (except API key)

Run: `python3 demo_journey.py`

### 7. **INTEGRATION_GUIDE.md**
Step-by-step guide:
- Database setup
- Route registration
- Configuration
- Troubleshooting

### 8. **README_SURGERY_DAY_BUILDER.md**
Complete documentation:
- Architecture overview
- Feature list
- API reference
- Security considerations
- Future roadmap

---

## 3-Step Quick Start

### Step 1: Test the Demo (2 minutes)
```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python3 demo_journey.py
```

Have a conversation like:
```
"I had Chiari surgery February 26, 2026. Recovery was tough but faith helped."
```

### Step 2: Integrate into Flask (20 minutes)
```bash
# 1. Copy files to your Flask app
cp models_health_journey.py app/models/
cp services_journey_generator.py app/services/
cp routes_journey.py app/routes/
cp templates_journey_*.html templates/journey/

# 2. Update app/__init__.py
from app.routes.journey import register_journey_routes
register_journey_routes(app)

# 3. Migrate database
flask db migrate -m "Add journey models"
flask db upgrade

# 4. Set environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# 5. Start Flask
flask run
```

### Step 3: Test in Browser (5 minutes)
```
http://localhost:5000/journey/builder
```

Click "Create Journey" and start describing your health story.

---

## What Happens When User Creates a Journey

```
1. User: "I had Chiari surgery Feb 26, 2026..."
   ↓
2. Claude: "How long was your recovery?" (asks clarifying questions)
   ↓
3. User: "About 6 weeks. Faith was really important."
   ↓
4. Claude: "Any family support moments?" (gathers more info)
   ↓
5. User: "My family was amazing. They helped with everything."
   ↓
6. Claude: *Generates structure*
   {
     "title": "Chiari Surgery Recovery",
     "stages": [
       {"name": "Pre-op", "color": "#5b8fa8"},
       {"name": "Surgery Day", "color": "#5b8fa8"},
       {"name": "Recovery", "color": "#a05c5c"}
     ],
     "timeline_entries": [
       {date: "2026-02-26", type: "clinical", title: "Surgery", content: "..."},
       {date: "2026-02-27", type: "faith", title: "Gratitude", content: "..."},
       {date: "2026-03-01", type: "family", title: "Support", content: "..."}
     ]
   }
   ↓
7. User clicks "Publish"
   ↓
8. Journey available at:
   /health-journey/chiari-surgery-recovery
```

---

## Core Features

### Phase 1 ✅ (Complete)
- [x] Chat interface for journey creation
- [x] Claude API multi-turn conversation
- [x] Auto-extract journey structure
- [x] Publish to timeline page
- [x] Comments & reactions (4 emoji types)
- [x] Privacy controls (public/semi-private/private)
- [x] Share links & embed code

### Phase 2 (Ready, just not built yet)
- [ ] SVG medical diagrams (code ready)
- [ ] AI photo captions
- [ ] Condition-specific color schemes
- [ ] More timeline entry suggestions

### Phase 3+
- [ ] PDF export
- [ ] Collaborative journeys
- [ ] Templates by condition
- [ ] Analytics
- [ ] Public directory

---

## Database Tables

### health_journeys (Main)
```sql
id (UUID)
user_id (FK) → users
slug (unique index)
title, condition, procedure_type
start_date, end_date
stages (JSON)
timeline_entries (JSON)
color_scheme (JSON)
privacy (public/semi-private/private)
share_token
is_published, is_deleted
created_at, updated_at
```

### journey_comments
```sql
id (UUID)
journey_id (FK) → health_journeys
user_name, user_email
comment (text)
reactions (JSON: array of {type, user_id, date})
is_approved, is_deleted
created_at, updated_at
```

---

## Key API Endpoints

### Chat
```
POST /api/journey/chat
Input:  {message, session_id}
Output: {response, journey_structure, needs_more_info, turn}
```

### Create Journey
```
POST /api/journey
Input:  {title, condition, stages, timeline_entries, ...}
Output: {id, slug, public_url, share_url, embed_code}
```

### View Journey
```
GET /health-journey/<slug>
GET /health-journey/<slug>?share_token=<token>  (for private)
```

### Comments
```
GET  /api/journey/<id>/comments
POST /api/journey/<id>/comments
```

---

## File Structure After Integration

```
pecksmission/
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   └── health_journey.py          ← NEW
│   ├── services/
│   │   └── journey_generator.py       ← NEW
│   ├── routes/
│   │   ├── public.py
│   │   ├── auth.py
│   │   └── journey.py                 ← NEW
│   └── extensions.py
├── templates/
│   ├── base.html
│   ├── surgery-day.html               ← EXISTING
│   └── journey/                       ← NEW FOLDER
│       ├── builder.html               ← NEW
│       └── view.html                  ← NEW
├── static/
│   └── css/                           ← Inline CSS in templates
├── migrations/
│   └── [auto-generated]
├── .env                               ← Add ANTHROPIC_API_KEY
├── requirements.txt                   ← Add anthropic
└── app.py                             ← Update __init__.py
```

---

## Configuration (.env)

```
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-20250805

# Optional journey config
JOURNEY_MAX_ENTRIES=50
JOURNEY_MAX_PHOTOS=100
JOURNEY_MAX_VIDEO_SIZE_MB=500
```

---

## Testing

### Test 1: Demo Script (No Flask)
```bash
python3 demo_journey.py
```
Creates a journey in your terminal, exports to JSON.

### Test 2: Flask Integration
```bash
pytest tests/test_journey.py -v
```

### Test 3: Manual Browser Test
1. Navigate to `/journey/builder`
2. Describe health journey
3. Claude should ask clarifying questions
4. After 3-4 exchanges, structure should generate
5. Click "Publish"
6. View at `/health-journey/[slug]`
7. Try commenting, reacting, sharing

---

## Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| `ANTHROPIC_API_KEY not found` | Export or add to `.env`, call `load_dotenv()` |
| `No module named 'anthropic'` | `pip install anthropic` |
| `No such table: health_journeys` | `flask db upgrade` |
| Template not found | Check `templates/journey/` exists |
| Claude API timeout | Wait a few seconds, retry |
| Comments not saving | Check `journey_comments` table exists |

---

## Integration with Existing Features

### Surgery Day Page
Your existing `/surgery-day.html` remains unchanged. The builder creates similar pages for other users.

### Blog Listing
```python
# In blog route, mix in public journeys:
posts = Post.query...
journeys = HealthJourney.query.filter_by(privacy='public')
all_content = list(posts) + list(journeys)
```

### Resources Section
```python
# Link condition-specific journeys:
journeys = HealthJourney.query.filter_by(
    condition=condition, 
    privacy='public'
)
```

### User Dashboard
```python
# Show user's journeys:
journeys = current_user.health_journeys
```

---

## Next Steps for Jonah

1. **Copy files** to your Flask app structure
2. **Update imports** in `app/__init__.py`
3. **Create database migration**
4. **Test with demo script** first (offline)
5. **Test in Flask** with http://localhost:5000/journey/builder
6. **Iterate** based on feedback

---

## Next Steps for Joe

1. **Test the demo** with your own health story
2. **Provide feedback** on:
   - AI questions (are they helpful?)
   - Generated structure (realistic?)
   - UI/UX (intuitive?)
3. **Test with 3-5 real users**
4. **Iterate** on Claude prompts based on feedback

---

## Support Resources

- **README_SURGERY_DAY_BUILDER.md** - Complete documentation
- **INTEGRATION_GUIDE.md** - Step-by-step integration
- **demo_journey.py** - Working example
- **Code comments** - Docstrings and inline comments

---

## Success Metrics

**Week 1:**
- [ ] Demo script runs without errors
- [ ] Flask integration complete
- [ ] Database migrations work
- [ ] Can create journey in browser

**Week 2:**
- [ ] 3+ test journeys created
- [ ] Comments working
- [ ] Share links functional
- [ ] Responsive on mobile

**Week 3:**
- [ ] User feedback collected
- [ ] Prompts refined
- [ ] Ready for wider launch

---

## Questions?

1. See **INTEGRATION_GUIDE.md** for setup help
2. See **README_SURGERY_DAY_BUILDER.md** for features
3. Run **demo_journey.py** to understand flow
4. Check code comments for implementation details

---

## Summary

You have everything needed to launch Surgery Day Builder:

✅ Complete backend (models, services, routes)
✅ Complete frontend (chat + view templates)
✅ Database schema with migrations
✅ Claude API integration (multi-turn)
✅ Privacy/sharing system
✅ Comments/reactions
✅ Standalone demo for testing
✅ Step-by-step integration guide
✅ Complete documentation

**Time to integration: 30 minutes**
**Time to first journey: 5 minutes after integration**

Good luck! 🚀

---

## Files to Copy

1. `models_health_journey.py` → `app/models/health_journey.py`
2. `services_journey_generator.py` → `app/services/journey_generator.py`
3. `routes_journey.py` → `app/routes/journey.py`
4. `templates_journey_builder.html` → `templates/journey/builder.html`
5. `templates_journey_view.html` → `templates/journey/view.html`
6. Keep `demo_journey.py` for testing

Optional:
- `README_SURGERY_DAY_BUILDER.md` - Reference
- `INTEGRATION_GUIDE.md` - Setup help

