"""
Surgery Day Builder - Complete Web Application
Main Flask application with all routes, database setup, and configuration

This is a production-ready web application where users can:
1. Create health journeys through AI chat
2. View published journey timelines
3. Comment and react to journeys
4. Share journeys with others
5. Manage their personal journeys
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://localhost/surgery_day_builder'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# File uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    
    # Profile
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    health_journeys = db.relationship('HealthJourney', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class HealthJourney(db.Model):
    """Health journey model"""
    __tablename__ = 'health_journeys'
    
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID, db.ForeignKey('users.id'), nullable=False, index=True)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Metadata
    title = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(255))
    procedure_type = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')
    
    # AI-generated content (JSON fields)
    summary = db.Column(db.Text)
    stages = db.Column(db.JSON, default=[])
    timeline_entries = db.Column(db.JSON, default=[])
    color_scheme = db.Column(db.JSON, default={})
    
    # Privacy & sharing
    privacy = db.Column(db.String(50), default='private')
    share_token = db.Column(db.String(255), unique=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Media
    gallery_photos = db.Column(db.JSON, default=[])
    videos = db.Column(db.JSON, default=[])
    diagrams = db.Column(db.JSON, default=[])
    
    # Stats
    view_count = db.Column(db.Integer, default=0)
    
    # Status
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='health_journeys')
    comments = db.relationship('JourneyComment', back_populates='journey', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<HealthJourney {self.slug}>'


class JourneyComment(db.Model):
    """Comment on a health journey"""
    __tablename__ = 'journey_comments'
    
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    journey_id = db.Column(db.UUID, db.ForeignKey('health_journeys.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Commenter
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255))
    
    # Content
    comment = db.Column(db.Text, nullable=False)
    reactions = db.Column(db.JSON, default=[])
    
    # Moderation
    is_approved = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    journey = db.relationship('HealthJourney', back_populates='comments')
    
    def __repr__(self):
        return f'<JourneyComment by {self.user_name}>'


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

auth_bp = __import__('flask').Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        
        # Validate
        if not data.get('email') or not data.get('username') or not data.get('password'):
            return {'error': 'Missing required fields'}, 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already registered'}, 400
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Username already taken'}, 400
        
        # Create user
        user = User(
            email=data['email'],
            username=data['username'],
            name=data.get('name', data['username'])
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        return redirect(url_for('journey.builder')) if request.method == 'GET' else {'success': True}
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and user.check_password(data.get('password')):
            login_user(user)
            return redirect(url_for('journey.builder')) if request.method == 'GET' else {'success': True}
        
        return {'error': 'Invalid email or password'}, 401
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('public.index'))


app.register_blueprint(auth_bp)

# ============================================================================
# PUBLIC ROUTES
# ============================================================================

public_bp = __import__('flask').Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Homepage"""
    # Show featured public journeys
    featured = HealthJourney.query.filter_by(
        privacy='public',
        is_published=True,
        is_deleted=False
    ).order_by(HealthJourney.view_count.desc()).limit(6).all()
    
    return render_template('public/index.html', featured_journeys=featured)


@public_bp.route('/about')
def about():
    """About page"""
    return render_template('public/about.html')


@public_bp.route('/resources')
def resources():
    """Healthcare resources"""
    return render_template('public/resources.html')


app.register_blueprint(public_bp)

# ============================================================================
# JOURNEY BUILDER ROUTES
# ============================================================================

journey_bp = __import__('flask').Blueprint('journey', __name__, url_prefix='/journey')

@journey_bp.route('/builder')
@login_required
def builder():
    """Journey creation chat interface"""
    if 'journey_session_id' not in session:
        session['journey_session_id'] = str(uuid.uuid4())
    
    return render_template('journey/builder.html', session_id=session['journey_session_id'])


@journey_bp.route('/dashboard')
@login_required
def dashboard():
    """User's journey dashboard"""
    journeys = HealthJourney.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(HealthJourney.created_at.desc()).all()
    
    return render_template('journey/dashboard.html', journeys=journeys)


@journey_bp.route('/<id>/edit')
@login_required
def edit_journey(id):
    """Edit journey"""
    journey = HealthJourney.query.get_or_404(id)
    
    # Check ownership
    if journey.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    return render_template('journey/edit.html', journey=journey)


app.register_blueprint(journey_bp)

# ============================================================================
# HEALTH JOURNEY ROUTES
# ============================================================================

health_bp = __import__('flask').Blueprint('health', __name__, url_prefix='/health-journey')

@health_bp.route('/<slug>')
def view_journey(slug):
    """View published health journey"""
    journey = HealthJourney.query.filter_by(slug=slug, is_deleted=False).first_or_404()
    
    # Check privacy
    share_token = request.args.get('share_token')
    
    if journey.privacy == 'private':
        if not share_token or share_token != journey.share_token:
            if not current_user.is_authenticated or journey.user_id != current_user.id:
                return {'error': 'Access denied'}, 403
    elif journey.privacy == 'semi-private':
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
    
    # Increment view count
    journey.view_count = (journey.view_count or 0) + 1
    db.session.commit()
    
    return render_template('journey/view.html', journey=journey)


@health_bp.route('/<slug>/share')
def share_journey(slug):
    """Share modal/page"""
    journey = HealthJourney.query.filter_by(slug=slug, is_deleted=False).first_or_404()
    
    return render_template('journey/share.html', journey=journey)


app.register_blueprint(health_bp)

# ============================================================================
# API ROUTES
# ============================================================================

api_bp = __import__('flask').Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/journey/chat', methods=['POST'])
@login_required
def chat():
    """Process chat message for journey creation"""
    from services.journey_generator import JourneyGenerator
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id')
    
    if not user_message:
        return {'error': 'Empty message'}, 400
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get or create generator for this session
    if 'generators' not in session:
        session['generators'] = {}
    
    if session_id not in session['generators']:
        session['generators'][session_id] = JourneyGenerator().__dict__
    
    # For now, we'll need to manage conversation history differently
    # In production, use Redis for session storage
    
    # Process with Claude
    from services.journey_generator import JourneyGenerator
    gen = JourneyGenerator()
    
    result = gen.process_user_input(user_message)
    
    return jsonify({
        'response': result['response'],
        'journey_structure': result['journey_structure'],
        'needs_more_info': result['needs_more_info'],
        'conversation_stage': result['conversation_stage'],
        'turn': result['turn']
    }), 200


@api_bp.route('/journey', methods=['POST'])
@login_required
def create_journey():
    """Create a journey from generated structure"""
    data = request.get_json()
    
    # Validate
    required = ['title', 'condition', 'start_date', 'stages', 'timeline_entries']
    if not all(field in data for field in required):
        return {'error': 'Missing required fields'}, 400
    
    # Create slug
    slug = data['title'].lower().replace(' ', '-')[:50]
    slug = f"{slug}-{str(uuid.uuid4())[:8]}"
    
    # Create journey
    journey = HealthJourney(
        user_id=current_user.id,
        slug=slug,
        title=data['title'],
        condition=data.get('condition'),
        procedure_type=data.get('procedure_type'),
        start_date=data['start_date'],
        end_date=data.get('end_date'),
        summary=data.get('summary'),
        stages=data['stages'],
        timeline_entries=data['timeline_entries'],
        color_scheme=data.get('color_scheme', {}),
        privacy=data.get('privacy', 'private'),
        share_token=str(uuid.uuid4()),
        is_published=True
    )
    
    db.session.add(journey)
    db.session.commit()
    
    return jsonify({
        'id': str(journey.id),
        'slug': journey.slug,
        'public_url': url_for('health.view_journey', slug=journey.slug, _external=True),
        'share_url': url_for('health.view_journey', slug=journey.slug, share_token=journey.share_token, _external=True)
    }), 201


@api_bp.route('/journey/<journey_id>/comments', methods=['GET', 'POST'])
def journey_comments(journey_id):
    """Get or add comments"""
    journey = HealthJourney.query.get_or_404(journey_id)
    
    if request.method == 'GET':
        comments = JourneyComment.query.filter_by(
            journey_id=journey_id,
            is_deleted=False
        ).order_by(JourneyComment.created_at.desc()).all()
        
        return jsonify([c.__dict__ for c in comments]), 200
    
    # POST - add comment
    data = request.get_json()
    
    if not data.get('user_name') or not data.get('comment'):
        return {'error': 'Missing required fields'}, 400
    
    comment = JourneyComment(
        journey_id=journey_id,
        user_name=data['user_name'],
        user_email=data.get('user_email'),
        comment=data['comment']
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({'success': True, 'comment_id': str(comment.id)}), 201


@api_bp.route('/journey/<journey_id>/upload-photo', methods=['POST'])
@login_required
def upload_photo(journey_id):
    """Upload photo to journey"""
    from werkzeug.utils import secure_filename
    
    journey = HealthJourney.query.get_or_404(journey_id)
    
    # Check ownership
    if journey.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    file = request.files.get('file')
    caption = request.form.get('caption', '')
    
    if not file or file.filename == '':
        return {'error': 'No file selected'}, 400
    
    # Save file
    filename = f"journey-{journey_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Add to gallery
    photo = {
        'url': f'/static/uploads/{filename}',
        'caption': caption,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    if not journey.gallery_photos:
        journey.gallery_photos = []
    
    journey.gallery_photos.append(photo)
    db.session.commit()
    
    return jsonify({'success': True, 'photo': photo}), 201


app.register_blueprint(api_bp)

# ============================================================================
# LOGIN MANAGER
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_user():
    return {'current_user': current_user}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
