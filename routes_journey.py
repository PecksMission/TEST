"""
Journey Builder Routes
Handles all HTTP endpoints for creating, viewing, editing, and sharing health journeys

Routes:
  GET  /journey/builder          - Chat interface for journey creation
  POST /api/journey/chat         - Process chat message
  GET  /health-journey/<slug>    - View published journey
  GET  /user/journeys            - User's journey dashboard
  POST /api/journey              - Create new journey
  PUT  /api/journey/<id>         - Update journey
  DELETE /api/journey/<id>       - Delete journey (soft delete)
  POST /api/journey/<id>/share   - Share journey
  GET  /api/journey/<id>/embed   - Get embed code
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, abort
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os
import json
from functools import wraps

# These would import from your actual app structure
# from app.extensions import db
# from app.models import HealthJourney, JourneyComment, User
# from app.auth import login_required, get_current_user
# from app.services.journey_generator import JourneyGenerator
# from app.utils.file_handler import upload_to_s3
# from app.utils.slugify import slugify

# Create blueprint
journey_bp = Blueprint('journey', __name__, url_prefix='/journey')
api_bp = Blueprint('api_journey', __name__, url_prefix='/api/journey')
health_journey_bp = Blueprint('health_journey', __name__, url_prefix='/health-journey')

# Initialize generator instance (would be singleton in real app)
generator = None  # Lazy loaded


def get_generator():
    """Get or create journey generator instance"""
    global generator
    if generator is None:
        from services_journey_generator import JourneyGenerator
        generator = JourneyGenerator()
    return generator


def get_session_generator(session_id: str):
    """
    Get generator for a specific session
    
    In production, store conversation history in Redis:
    redis.set(f"journey:session:{session_id}", json.dumps(history), ex=3600)
    """
    # For now, store in Flask session
    if 'journey_sessions' not in session:
        session['journey_sessions'] = {}
    
    if session_id not in session['journey_sessions']:
        from services_journey_generator import JourneyGenerator
        session['journey_sessions'][session_id] = {
            'generator': JourneyGenerator(),
            'created_at': datetime.utcnow().isoformat()
        }
    
    return session['journey_sessions'][session_id]['generator']


# ============================================================================
# JOURNEY BUILDER - Chat Interface
# ============================================================================

@journey_bp.route('/builder', methods=['GET'])
def builder():
    """
    GET /journey/builder
    Display chat interface for creating a new journey
    """
    # Generate or get session ID
    if 'journey_session_id' not in session:
        session['journey_session_id'] = str(uuid.uuid4())
    
    return render_template('journey/builder.html', session_id=session['journey_session_id'])


@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    POST /api/journey/chat
    
    Process user input in journey creation chat
    
    Request JSON:
    {
        "message": "I had Chiari surgery...",
        "session_id": "uuid"
    }
    
    Response JSON:
    {
        "response": "AI response text",
        "journey_structure": {journey data} or null,
        "needs_more_info": true/false,
        "conversation_stage": "gathering|clarifying|complete",
        "turn": 2
    }
    """
    data = request.get_json()
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', session.get('journey_session_id'))
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    if not session_id:
        session_id = str(uuid.uuid4())
        session['journey_session_id'] = session_id
    
    # Get generator for this session
    gen = get_session_generator(session_id)
    
    # Process input
    result = gen.process_user_input(user_message)
    
    # Convert to JSON-serializable
    response_data = {
        'response': result['response'],
        'journey_structure': result['journey_structure'],
        'needs_more_info': result['needs_more_info'],
        'conversation_stage': result['conversation_stage'],
        'turn': result['turn'],
        'session_id': session_id
    }
    
    return jsonify(response_data), 200


# ============================================================================
# JOURNEY MANAGEMENT
# ============================================================================

@api_bp.route('', methods=['POST'])
def create_journey():
    """
    POST /api/journey
    
    Create a new journey from the generated structure
    
    Request JSON:
    {
        "title": "Chiari Surgery Recovery",
        "condition": "Chiari Type I",
        "procedure_type": "Craniectomy",
        "start_date": "2026-02-26",
        "end_date": "2026-03-15",
        "stages": [...],
        "timeline_entries": [...],
        "color_scheme": {...},
        "privacy": "private",
        "session_id": "uuid"
    }
    
    Response JSON:
    {
        "id": "journey-uuid",
        "slug": "chiari-surgery-recovery",
        "public_url": "https://pecksmission.com/health-journey/chiari-surgery-recovery",
        "share_url": "https://pecksmission.com/health-journey/chiari-surgery-recovery?share_token=...",
        "embed_code": "<iframe src=\"...\"></iframe>"
    }
    """
    # In real app: @login_required decorator would ensure user is logged in
    # current_user = get_current_user()
    
    data = request.get_json()
    
    # Validate required fields
    required = ['title', 'condition', 'start_date', 'stages', 'timeline_entries']
    if not all(field in data for field in required):
        return jsonify({'error': f'Missing required fields: {", ".join(required)}'}), 400
    
    # Create slug from title
    slug = create_slug(data['title'])
    
    # Check slug uniqueness (in real app: check DB)
    # existing = HealthJourney.query.filter_by(slug=slug).first()
    # if existing:
    #     slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    
    # Create journey dict (would be saved to DB)
    journey = {
        'id': str(uuid.uuid4()),
        'user_id': 'current_user_id',  # Would be current_user.id
        'slug': slug,
        'title': data['title'],
        'condition': data.get('condition'),
        'procedure_type': data.get('procedure_type'),
        'start_date': data['start_date'],
        'end_date': data.get('end_date'),
        'stages': data['stages'],
        'timeline_entries': data['timeline_entries'],
        'color_scheme': data.get('color_scheme', {}),
        'privacy': data.get('privacy', 'private'),
        'share_token': str(uuid.uuid4()) if data.get('privacy') != 'public' else None,
        'is_published': True,
        'created_at': datetime.utcnow().isoformat(),
    }
    
    # In real app: would save to database
    # journey_obj = HealthJourney(**journey)
    # db.session.add(journey_obj)
    # db.session.commit()
    
    # Clear session
    if 'journey_session_id' in session:
        if 'journey_sessions' in session and session['journey_session_id'] in session['journey_sessions']:
            del session['journey_sessions'][session['journey_session_id']]
    
    return jsonify({
        'id': journey['id'],
        'slug': journey['slug'],
        'public_url': url_for('health_journey.view_journey', slug=slug, _external=True),
        'share_url': url_for('health_journey.view_journey', slug=slug, share_token=journey['share_token'], _external=True),
        'embed_code': f'<iframe src="{url_for("health_journey.view_journey", slug=slug, _external=True)}" width="100%" height="1200" frameborder="0" title="{journey["title"]}"></iframe>',
        'success': True
    }), 201


@api_bp.route('/<journey_id>', methods=['PUT'])
def update_journey(journey_id):
    """
    PUT /api/journey/<journey_id>
    
    Update an existing journey (owner only)
    """
    data = request.get_json()
    
    # In real app:
    # journey = HealthJourney.query.get_or_404(journey_id)
    # current_user = get_current_user()
    # if journey.user_id != current_user.id:
    #     abort(403)
    
    # Update fields
    updatable = ['title', 'stages', 'timeline_entries', 'color_scheme', 'privacy', 'is_published']
    for field in updatable:
        if field in data:
            # journey[field] = data[field]
            pass
    
    # journey.updated_at = datetime.utcnow()
    # db.session.commit()
    
    return jsonify({'success': True, 'message': 'Journey updated'}), 200


@api_bp.route('/<journey_id>', methods=['DELETE'])
def delete_journey(journey_id):
    """
    DELETE /api/journey/<journey_id>
    
    Delete a journey (soft delete - mark as deleted but keep data)
    """
    # In real app:
    # journey = HealthJourney.query.get_or_404(journey_id)
    # journey.is_deleted = True
    # db.session.commit()
    
    return jsonify({'success': True, 'message': 'Journey deleted'}), 200


# ============================================================================
# VIEWING JOURNEYS
# ============================================================================

@health_journey_bp.route('/<slug>', methods=['GET'])
def view_journey(slug):
    """
    GET /health-journey/<slug>
    
    View a published journey
    
    URL parameters:
      ?share_token=uuid  - For private journeys
    """
    # In real app:
    # journey = HealthJourney.query.filter_by(slug=slug, is_deleted=False).first_or_404()
    
    # Check privacy
    share_token = request.args.get('share_token')
    # if journey.privacy == 'private' and journey.share_token != share_token:
    #     if not is_owner(journey):
    #         abort(403)
    
    # Increment view count (in real app)
    # journey.view_count = (journey.view_count or 0) + 1
    # db.session.commit()
    
    # In real app: Fetch journey from DB
    # For demo, would pass journey object to template
    
    return render_template('journey/view.html', slug=slug)


@health_journey_bp.route('/<slug>/embed', methods=['GET'])
def embed_journey(slug):
    """
    GET /health-journey/<slug>/embed
    
    Get embed code for this journey
    """
    # In real app: fetch from DB
    # journey = HealthJourney.query.filter_by(slug=slug).first_or_404()
    
    url = url_for('health_journey.view_journey', slug=slug, _external=True)
    embed_code = f'<iframe src="{url}" width="100%" height="1200" frameborder="0" title="{slug}"></iframe>'
    
    return jsonify({'embed_code': embed_code}), 200


# ============================================================================
# SHARING
# ============================================================================

@api_bp.route('/<journey_id>/share', methods=['POST'])
def share_journey(journey_id):
    """
    POST /api/journey/<journey_id>/share
    
    Share journey with recipients via email
    
    Request JSON:
    {
        "emails": ["recipient@example.com"],
        "message": "Check out my health journey...",
        "privacy": "semi-private"
    }
    """
    data = request.get_json()
    emails = data.get('emails', [])
    
    # In real app:
    # journey = HealthJourney.query.get_or_404(journey_id)
    # current_user = get_current_user()
    # if journey.user_id != current_user.id:
    #     abort(403)
    
    # Generate share token if needed
    # if data.get('privacy') == 'private':
    #     journey.share_token = str(uuid.uuid4())
    #     db.session.commit()
    
    # Send emails
    share_url = url_for('health_journey.view_journey', slug='example-slug', _external=True)
    for email in emails:
        # send_share_email(
        #     to=email,
        #     title=journey.title,
        #     share_url=share_url,
        #     message=data.get('message', '')
        # )
        pass
    
    return jsonify({
        'success': True,
        'message': f'Shared with {len(emails)} recipients',
        'share_url': share_url
    }), 200


# ============================================================================
# COMMENTS & REACTIONS
# ============================================================================

@api_bp.route('/<journey_id>/comments', methods=['GET'])
def get_comments(journey_id):
    """
    GET /api/journey/<journey_id>/comments
    
    Get all comments for a journey
    
    Query parameters:
      ?page=1&limit=20
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # In real app:
    # journey = HealthJourney.query.get_or_404(journey_id)
    # comments = JourneyComment.query.filter_by(journey_id=journey_id, is_deleted=False)\
    #     .order_by(JourneyComment.created_at.desc())\
    #     .paginate(page=page, per_page=limit)
    
    return jsonify({
        'comments': [],  # Would be serialized comments
        'total': 0,
        'page': page,
        'pages': 1
    }), 200


@api_bp.route('/<journey_id>/comments', methods=['POST'])
def add_comment(journey_id):
    """
    POST /api/journey/<journey_id>/comments
    
    Add a comment to a journey
    
    Request JSON:
    {
        "user_name": "Jane Doe",
        "user_email": "jane@example.com",
        "comment": "What an inspiring journey...",
        "entry_id": null  # Optional: comment on specific entry
    }
    """
    data = request.get_json()
    
    # Validate
    if not data.get('user_name') or not data.get('comment'):
        return jsonify({'error': 'Name and comment required'}), 400
    
    # In real app:
    # journey = HealthJourney.query.get_or_404(journey_id)
    # 
    # comment = JourneyComment(
    #     journey_id=journey_id,
    #     user_name=data['user_name'],
    #     user_email=data.get('user_email'),
    #     comment=data['comment'],
    #     entry_id=data.get('entry_id')
    # )
    # db.session.add(comment)
    # db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Comment added',
        'comment_id': str(uuid.uuid4())
    }), 201


@api_bp.route('/<journey_id>/comments/<comment_id>/react', methods=['POST'])
def react_to_comment(journey_id, comment_id):
    """
    POST /api/journey/<journey_id>/comments/<comment_id>/react
    
    Add a reaction to a comment
    
    Request JSON:
    {
        "reaction_type": "heart"  # heart, hug, encouragement, celebration
    }
    """
    data = request.get_json()
    reaction_type = data.get('reaction_type')
    
    allowed = ['heart', 'hug', 'encouragement', 'celebration']
    if reaction_type not in allowed:
        return jsonify({'error': f'Invalid reaction type. Must be one of {allowed}'}), 400
    
    # In real app:
    # comment = JourneyComment.query.get_or_404(comment_id)
    # comment.reactions.append({
    #     'type': reaction_type,
    #     'user_id': get_current_user().id if logged in else 'anonymous',
    #     'created_at': datetime.utcnow().isoformat()
    # })
    # db.session.commit()
    
    return jsonify({'success': True, 'reaction_type': reaction_type}), 200


# ============================================================================
# USER DASHBOARD
# ============================================================================

@journey_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    GET /journey/dashboard
    
    Show user's journeys
    Requires authentication
    """
    # In real app: @login_required
    # current_user = get_current_user()
    # journeys = HealthJourney.query.filter_by(user_id=current_user.id, is_deleted=False)\
    #     .order_by(HealthJourney.created_at.desc())\
    #     .all()
    
    return render_template('journey/dashboard.html', journeys=[])


# ============================================================================
# HELPERS
# ============================================================================

def create_slug(title: str) -> str:
    """
    Convert title to URL-safe slug
    
    Example: "Chiari Surgery Recovery" -> "chiari-surgery-recovery"
    """
    import re
    # Lowercase and replace spaces with hyphens
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens with single hyphen
    slug = slug.strip('-')                 # Remove leading/trailing hyphens
    return slug


def is_owner(journey, current_user=None):
    """Check if current user owns the journey"""
    if current_user is None:
        from flask import g
        current_user = g.get('current_user')
    
    return current_user and journey.user_id == current_user.id


# ============================================================================
# Register blueprints
# ============================================================================

def register_journey_routes(app):
    """Register all journey routes with the Flask app"""
    app.register_blueprint(journey_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(health_journey_bp)


# Example in main app.py:
# from routes.journey import register_journey_routes
# register_journey_routes(app)
