# Surgery Day Builder — Implementation Roadmap

## Phase 1: MVP (Week 1-2)
Goal: Minimal working system for one user to create a journey through chat.

### Backend
- [ ] Create `JourneyGenerator` service with Claude API integration
  - Multi-turn conversation system (store conversation history)
  - System prompt: compassionate healthcare storyteller
  - Prompt user to describe: condition, dates, milestones
  - Extract structured JSON from responses
- [ ] Create `HealthJourney` model in SQLAlchemy
  - id, user_id, slug, title, condition, start_date, end_date
  - stages (JSON), timeline_entries (JSON), color_scheme (JSON)
  - privacy, share_token, is_published
- [ ] Create `/journey/builder` route (GET) — renders chat interface
- [ ] Create `/api/journey/chat` route (POST) — processes messages, returns AI response + structure
- [ ] Create `/health-journey/<slug>` route (GET) — renders journey page from template

### Frontend
- [ ] Chat interface (`/templates/surgery-day-builder/chat.html`)
  - Messages display (user + assistant)
  - Textarea input + send button
  - Real-time preview panel (updates as user provides data)
- [ ] Journey page template (`/templates/surgery-day-builder/journey-page.html`)
  - Mimics Surgery Day layout: header, progress board, timeline, comments
  - Responsive CSS (mobile-first)
  - Inline CSS (no external stylesheet initially)

### Database
- [ ] Create migration for `health_journeys` table
- [ ] Create migration for `journey_entries` table (optional for MVP)

### Testing
- [ ] Manual: Chat with one test health journey
- [ ] Verify: Generated page renders correctly
- [ ] Edge cases: Empty inputs, malformed JSON from Claude

---

## Phase 2: Content Generation (Week 2-3)
Goal: AI auto-generates timeline entries, color schemes, and basic diagrams.

### Backend
- [ ] Extend `JourneyGenerator` with:
  - `generate_timeline_entries()` — creates 5-10 suggested entries from journey info
  - `generate_color_scheme()` — picks colors based on condition (clinical=blue, faith=red, family=gold)
  - `generate_svg_diagram()` — asks Claude to create simple medical diagram for condition
- [ ] Store generated content in `health_journeys.timeline_entries`, `color_scheme`, `diagrams` JSON fields
- [ ] Create `/api/journey/<id>/regenerate` route — user can regenerate content

### Frontend
- [ ] Preview panel updates with:
  - Generated stages + colors
  - Sample timeline entries (user can edit/delete)
  - Generated diagram preview

### Testing
- [ ] Verify: Color scheme changes per condition
- [ ] Verify: SVG diagrams render (no JS errors)
- [ ] Verify: Timeline entries are grammatically correct

---

## Phase 3: Media Upload & Captions (Week 3)
Goal: Users can upload photos/videos; AI generates captions.

### Backend
- [ ] S3 upload integration
  - Create S3 bucket for journey media
  - Create signed upload URLs (client → S3 direct)
  - Store media metadata in `health_journeys.gallery_photos` JSON
- [ ] Extend `JourneyGenerator`:
  - `generate_photo_captions()` — Claude describes photo, suggests caption
- [ ] Create `/api/journey/<id>/upload-photo` route (POST)
  - Receives file, generates caption, stores in DB
- [ ] Create `/api/journey/<id>/gallery` route (GET) — list all media

### Frontend
- [ ] Photo uploader in chat interface
  - Drag-and-drop or click-to-upload
  - Shows progress, generated caption
  - Add to gallery or delete
- [ ] Gallery section in journey page
  - Photo grid with captions
  - Mobile-responsive (CSS Grid)

### Testing
- [ ] Upload various image formats (JPG, PNG, WebP)
- [ ] Verify: Captions are meaningful
- [ ] Verify: Mobile layout works

---

## Phase 4: Share & Privacy (Week 4)
Goal: Users can share journeys, control access levels.

### Backend
- [ ] Create `/api/journey/<id>/share` route (POST)
  - Generate `share_token` (random UUID)
  - Return share URL: `/health-journey/[slug]?share_token=[token]`
  - Return embed code: `<iframe src="..."></iframe>`
- [ ] Create `/api/journey/<id>/privacy` route (PUT)
  - Set privacy level: public, semi-private, private
  - Validate ownership
- [ ] Update `/health-journey/<slug>` route:
  - Check privacy level + share_token
  - Return 403 if not accessible
- [ ] Create email notifications (optional)
  - Send share link to list of emails
  - Include personalized message from author

### Frontend
- [ ] Share modal in journey page header
  - Copy share link button
  - Copy embed code button
  - Email list input + send
- [ ] Privacy selector in edit view
  - Radio buttons: Public / Semi-Private / Private
  - Show access level on published page

### Testing
- [ ] Verify: Public journeys are Google-indexable (set robots meta)
- [ ] Verify: Private journeys return 403 without share_token
- [ ] Verify: Share links work
- [ ] Verify: Embed code works in iframe

---

## Phase 5: Comments & Community (Week 4-5)
Goal: Support messages, reactions on journeys.

### Backend
- [ ] Create `journey_comments` table
  - id, journey_id, entry_id, user_name, user_email, comment, reaction_type, created_at
- [ ] Create `/api/journey/<id>/comments` route (GET/POST)
  - GET: List all comments (paginated)
  - POST: Add new comment (store in DB, no auth required for now)
- [ ] Optional: Firestore integration (if preferred over PostgreSQL)

### Frontend
- [ ] Comments section in journey page
  - List of comments (name, date, message)
  - Reaction buttons: ❤️ 🤗 💪 🎉
  - Comment form: name, email, message
  - Real-time update when new comment posted (polling or WebSocket)

### Testing
- [ ] Post comment, verify it appears
- [ ] Click reaction, verify count updates
- [ ] Test mobile comment form

---

## Phase 6: User Dashboard & Management (Week 5)
Goal: Users can see all their journeys, edit, delete.

### Backend
- [ ] Create `/user/journeys` route (GET)
  - Show all journeys for logged-in user
  - Statuses: draft, published, completed
  - Edit, delete, duplicate, view actions
- [ ] Create `/api/journey/<id>` routes (DELETE, PUT)
  - DELETE: Soft-delete (mark is_deleted, don't show)
  - PUT: Update title, privacy, color_scheme, etc.

### Frontend
- [ ] Dashboard page (`/user/journeys`)
  - Card grid of user's journeys
  - Status badges (Draft, Published, Active, Completed)
  - Action buttons (View, Edit, Share, Delete)
- [ ] Edit page (`/journey/<id>/edit`)
  - Edit title, description, timeline entries
  - Regenerate colors/diagram
  - Preview on right

### Testing
- [ ] Verify: User can only see their own journeys
- [ ] Verify: Delete works (soft-delete, not visible)
- [ ] Verify: Edit persists correctly

---

## Phase 7: Advanced Features (Week 6+)

### Backend
- [ ] Multi-turn editing: User can ask AI to revise entries
  - "Make the surgery day entry more emotional"
  - "Add more faith/family moments"
  - AI regenerates and updates
- [ ] Export as PDF
  - Convert journey to PDF with formatting, images
  - Include share/attribution footer
- [ ] Integration with `/resources` section
  - If journey is public + condition-tagged, feature in resources
  - E.g., "Cancer Recovery Stories" section links to public cancer journeys
- [ ] Analytics
  - Track: views, reactions, comments, shares
  - Show user: "Your journey has 247 views"

### Frontend
- [ ] Rich text editor for timeline entries
  - Bold, italic, links, lists
  - Inline media (photos, videos)
- [ ] Stage builder UI
  - Drag-to-reorder stages
  - Add/remove stages
  - Edit color per stage
- [ ] Timeline entry builder
  - WYSIWYG editor for content
  - Type selector (clinical/faith/family/milestone)
  - Date picker
  - Media uploader for that entry

---

## Database Migrations (SQL)

```sql
-- Initial schema for Phase 1
CREATE TABLE health_journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    condition VARCHAR(255),
    procedure_type VARCHAR(255),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'draft', -- planning, active, completed
    
    -- AI-generated content (JSON)
    summary TEXT,
    stages JSONB DEFAULT '[]'::jsonb, -- [{name, description, color}]
    timeline_entries JSONB DEFAULT '[]'::jsonb, -- [{date, type, title, content, media}]
    color_scheme JSONB DEFAULT '{}'::jsonb, -- {clinical, faith, family, accent}
    
    -- Privacy & sharing
    privacy VARCHAR(50) DEFAULT 'private', -- private, semi-private, public
    share_token VARCHAR(255),
    is_published BOOLEAN DEFAULT false,
    
    -- Media
    gallery_photos JSONB DEFAULT '[]'::jsonb,
    videos JSONB DEFAULT '[]'::jsonb,
    diagrams JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX idx_journey_user_id ON health_journeys(user_id);
CREATE INDEX idx_journey_slug ON health_journeys(slug);
CREATE INDEX idx_journey_privacy ON health_journeys(privacy);

-- Phase 5: Comments table
CREATE TABLE journey_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES health_journeys(id) ON DELETE CASCADE,
    entry_id UUID, -- Optional: comment on specific entry (Phase 2)
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    comment TEXT NOT NULL,
    reaction_type VARCHAR(50), -- heart, hug, encouragement, celebration
    created_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false
);

CREATE INDEX idx_comment_journey_id ON journey_comments(journey_id);
```

---

## Configuration for Claude API

```python
# app/config.py or .env

ANTHROPIC_API_KEY = "sk-ant-..."
CLAUDE_MODEL = "claude-opus-4-20250805"

# For Surgery Day Builder specifically
JOURNEY_MAX_ENTRIES = 50
JOURNEY_MAX_PHOTOS = 100
JOURNEY_MAX_VIDEO_SIZE_MB = 500
GENERATE_DIAGRAMS = True  # Enable SVG diagram generation
```

---

## Testing Checklist

### Unit Tests
- [ ] `JourneyGenerator.process_user_input()` returns response + structure
- [ ] `JourneyGenerator._extract_journey_json()` parses JSON correctly
- [ ] `JourneyGenerator.generate_color_scheme()` returns valid color dict
- [ ] Models: `HealthJourney` CRUD operations

### Integration Tests
- [ ] Chat flow: User input → AI response → structure extracted → DB saved
- [ ] Journey page renders with all sections: header, timeline, comments
- [ ] Privacy: Private journeys return 403 without share_token
- [ ] Media upload → caption generation → gallery display

### E2E Tests (Selenium/Cypress)
- [ ] User creates journey via chat → sees preview → journey published
- [ ] User shares journey → recipient clicks link → can view
- [ ] User edits journey → changes persist
- [ ] Visitor posts comment on public journey → comment appears

---

## Deployment Considerations

### Secrets & Env Vars
```bash
ANTHROPIC_API_KEY
DATABASE_URL
AWS_ACCESS_KEY_ID (for S3)
AWS_SECRET_ACCESS_KEY
S3_BUCKET_NAME
FIREBASE_PROJECT_ID (optional, if using for comments)
```

### Performance
- [ ] Cache journeys in Redis (popular/recent)
- [ ] CDN for gallery photos (CloudFront / Cloudflare)
- [ ] Paginate comments (20 per page)
- [ ] Lazy-load images in gallery

### Security
- [ ] SQL injection: Use parameterized queries (SQLAlchemy does this)
- [ ] CSRF: Add Flask-WTF CSRF tokens
- [ ] XSS: Sanitize user input (Bleach library)
- [ ] File upload: Validate file type + size, rename files
- [ ] Private journeys: Validate share_token on every access

---

## Success Metrics

### Week 2 (MVP)
- [ ] Can create journey via chat
- [ ] Journey page renders
- [ ] All routes tested manually

### Week 4
- [ ] Users can share journeys
- [ ] Comments working
- [ ] Dashboard page finished

### Week 6
- [ ] 10+ test journeys created
- [ ] Average load time < 2s
- [ ] Mobile responsiveness verified

### Month 2
- [ ] Features: PDF export, AI revision, analytics
- [ ] Performance: < 1s page load
- [ ] User retention: Users come back to edit

---

## Future Ideas (Post-MVP)

1. **Collaborative Journeys** — Multiple users (patient + family + clinician) co-author
2. **Condition-Specific Templates** — "Pre-built stages for Chiari surgery" (Chiari → craniectomy → laminectomy → duraplasty)
3. **Integration with Peck's Mission Resources** — Link to condition-specific articles/podcasts
4. **Community Journeys Dashboard** — Public journeys organized by condition
5. **AI Reflection Prompts** — "What did you learn this week?" → Claude helps articulate
6. **Clinician Annotations** — Doctor can add clinical notes to timeline
7. **Export Formats** — PDF, EPUB, print-friendly
8. **Social Sharing** — Auto-generate quote graphics for Instagram/Twitter
9. **Multi-language Support** — Translate journey to Spanish, French, etc.
10. **Podcast Integration** — Audio narration of journey (TTS)

---

## Questions for Joe

1. Should comments require authentication or allow anonymous?
   - (MVP: anonymous, moderated by author)
2. Do you want Stripe integration for "tip the creator"?
   - (Deferred to Phase 7)
3. Should diagrams be AI-generated SVG or upload custom images?
   - (MVP: Claude-generated SVG based on description)
4. Do you want email notifications to commenters?
   - (Phase 5+)
5. Should journeys be harvestable into `/resources` section?
   - (Phase 7, if public + condition-tagged)

