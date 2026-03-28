"""
Health Journey Model - for Surgery Day Builder
Part of Peck's Mission healthcare storytelling platform
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Date, Boolean, JSON, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

# Base should be imported from your app - this shows the structure
# from app.extensions import db

class JourneyStatus(enum.Enum):
    """Status of a health journey"""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    DRAFT = "draft"

class JourneyPrivacy(enum.Enum):
    """Privacy level of a health journey"""
    PUBLIC = "public"
    SEMI_PRIVATE = "semi-private"
    PRIVATE = "private"

class HealthJourney:
    """
    Represents a user's health journey timeline
    
    A journey is a structured narrative of a medical condition or procedure,
    with stages (pre-op, surgery, recovery, etc.) and timeline entries
    (posts, reflections, milestones).
    
    Can be created via AI chat interface or manually edited.
    Supports media (photos, videos), reactions, and community comments.
    
    Example:
        journey = HealthJourney(
            user_id=user.id,
            title="Chiari Malformation Surgery",
            condition="Chiari Type I",
            start_date=date(2026, 2, 26),
            end_date=date(2026, 3, 5)
        )
    """
    
    # Core identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    
    # Journey metadata
    title = Column(String(255), nullable=False)
    condition = Column(String(255))  # e.g., "Chiari malformation", "Breast cancer"
    procedure_type = Column(String(255))  # e.g., "Craniectomy", "Mastectomy"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # Optional - for ongoing journeys
    status = Column(Enum(JourneyStatus), default=JourneyStatus.DRAFT)
    
    # Summary/description (short overview)
    summary = Column(Text)
    
    # AI-generated structured content (stored as JSON)
    # stages: [{name: "Pre-op", description: "...", color: "#5b8fa8"}, ...]
    stages = Column(JSON, default=[])
    
    # timeline_entries: [{date: "2026-02-26", type: "clinical", title: "...", content: "...", media: [...]}, ...]
    timeline_entries = Column(JSON, default=[])
    
    # color_scheme: {clinical: "#5b8fa8", faith: "#a05c5c", family: "#c9a84c", accent: "#c9a84c"}
    color_scheme = Column(JSON, default={
        "clinical": "#5b8fa8",
        "faith": "#a05c5c",
        "family": "#c9a84c",
        "accent": "#c9a84c"
    })
    
    # Privacy & sharing
    privacy = Column(Enum(JourneyPrivacy), default=JourneyPrivacy.PRIVATE)
    share_token = Column(String(255), unique=True)  # For shareable links (UUID)
    is_published = Column(Boolean, default=False)
    
    # Media galleries
    # gallery_photos: [{url: "...", caption: "...", date: "2026-02-26", alt_text: "..."}, ...]
    gallery_photos = Column(JSON, default=[])
    
    # videos: [{url: "...", title: "...", thumbnail: "...", caption: "..."}, ...]
    videos = Column(JSON, default=[])
    
    # diagrams: [{svg: "<svg>...</svg>", description: "...", procedure_step: 1}, ...]
    diagrams = Column(JSON, default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    
    # Relationships
    user = relationship("User", back_populates="health_journeys")
    comments = relationship("JourneyComment", back_populates="journey", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_slug', 'slug'),
        Index('idx_privacy', 'privacy'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<HealthJourney {self.slug}: {self.title}>"
    
    @property
    def entry_count(self):
        """Number of timeline entries"""
        return len(self.timeline_entries) if self.timeline_entries else 0
    
    @property
    def comment_count(self):
        """Number of comments on this journey"""
        return len([c for c in self.comments if not c.is_deleted])
    
    @property
    def reaction_count(self):
        """Total number of reactions"""
        return sum(len(c.reactions or []) for c in self.comments if c.reactions)
    
    @property
    def public_url(self):
        """Full URL for this journey"""
        from flask import url_for
        return url_for('journey.view_journey', slug=self.slug, _external=True)
    
    @property
    def share_url(self):
        """Share URL for private journeys"""
        if self.share_token:
            from flask import url_for
            return url_for('journey.view_journey', slug=self.slug, share_token=self.share_token, _external=True)
        return self.public_url
    
    @property
    def embed_code(self):
        """HTML embed code for blogs/websites"""
        return f'<iframe src="{self.public_url}" width="100%" height="1200" frameborder="0" title="{self.title}"></iframe>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'slug': self.slug,
            'title': self.title,
            'condition': self.condition,
            'procedure_type': self.procedure_type,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value,
            'summary': self.summary,
            'stages': self.stages,
            'timeline_entries': self.timeline_entries,
            'color_scheme': self.color_scheme,
            'privacy': self.privacy.value,
            'is_published': self.is_published,
            'entry_count': self.entry_count,
            'comment_count': self.comment_count,
            'reaction_count': self.reaction_count,
            'gallery_photos': self.gallery_photos,
            'videos': self.videos,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'public_url': self.public_url,
        }


class JourneyComment:
    """
    A comment or reaction on a health journey
    
    Users can post supportive messages and reactions.
    Comments are moderated by the journey author.
    
    Reactions: heart (❤), hug (🤗), encouragement (💪), celebration (🎉)
    """
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id = Column(UUID(as_uuid=True), ForeignKey('health_journeys.id', ondelete='CASCADE'), nullable=False)
    entry_id = Column(String(255))  # Optional: reference to specific timeline entry by date
    
    # Commenter info (anonymous or logged-in)
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255))  # Optional
    
    # Content
    comment = Column(Text, nullable=False)
    reactions = Column(JSON, default=[])  # [{type: "heart", user_id: "...", created_at: "..."}, ...]
    
    # Moderation
    is_approved = Column(Boolean, default=True)  # Author can moderate
    is_deleted = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    journey = relationship("HealthJourney", back_populates="comments")
    
    __table_args__ = (
        Index('idx_journey_id', 'journey_id'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<JourneyComment by {self.user_name} on {self.created_at}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'user_name': self.user_name,
            'user_email': self.user_email,
            'comment': self.comment,
            'reactions': self.reactions,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat(),
        }


# For SQLAlchemy with Flask-SQLAlchemy, the actual implementation would be:
"""
from app.extensions import db

class HealthJourney(db.Model):
    __tablename__ = 'health_journeys'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # ... (all fields as defined above)
    
    user = db.relationship("User", back_populates="health_journeys")
    comments = db.relationship("JourneyComment", back_populates="journey", cascade="all, delete-orphan")


class JourneyComment(db.Model):
    __tablename__ = 'journey_comments'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('health_journeys.id', ondelete='CASCADE'), nullable=False)
    
    # ... (all fields as defined above)
    
    journey = db.relationship("HealthJourney", back_populates="comments")
"""
