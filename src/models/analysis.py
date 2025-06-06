"""
Analysis models for tasks, domain results, and reports
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class AnalysisTask(db.Model):
    __tablename__ = 'analysis_tasks'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    progress = db.Column(db.Integer, default=0)
    current_domain = db.Column(db.String(255))
    error_message = db.Column(db.Text)
    domains_count = db.Column(db.Integer, default=0)
    use_test_data = db.Column(db.Boolean, default=False)
    ai_analysis_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    domain_results = db.relationship('DomainResult', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_name': self.task_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'current_domain': self.current_domain,
            'error_message': self.error_message,
            'domains_count': self.domains_count,
            'use_test_data': self.use_test_data,
            'ai_analysis_enabled': self.ai_analysis_enabled,
            'results': [result.to_dict() for result in self.domain_results]
        }

class DomainResult(db.Model):
    __tablename__ = 'domain_results'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey('analysis_tasks.id'), nullable=False)
    domain_name = db.Column(db.String(255), nullable=False)
    
    # Wayback Machine data
    has_snapshot = db.Column(db.Boolean)
    availability_ts = db.Column(db.String(20))
    total_snapshots = db.Column(db.Integer)
    timemap_count = db.Column(db.Integer)
    first_snapshot = db.Column(db.DateTime)
    last_snapshot = db.Column(db.DateTime)
    avg_interval_days = db.Column(db.Float)
    max_gap_days = db.Column(db.Integer)
    years_covered = db.Column(db.Integer)
    snapshots_per_year = db.Column(db.Text)  # JSON string
    unique_versions = db.Column(db.Integer)
    is_good = db.Column(db.Boolean)
    recommended = db.Column(db.Boolean)
    analysis_time_sec = db.Column(db.Float)
    
    # AI Analysis data
    thematic_analysis_result = db.Column(db.Text)  # JSON string
    ai_category = db.Column(db.String(100))
    ai_confidence = db.Column(db.Float)
    ai_description = db.Column(db.Text)
    
    # SEO metrics
    seo_metrics = db.Column(db.Text)  # JSON string
    assessment_score = db.Column(db.Float)
    assessment_summary = db.Column(db.Text)
    
    # Selection state
    is_selected = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert domain result to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'domain_name': self.domain_name,
            'has_snapshot': self.has_snapshot,
            'availability_ts': self.availability_ts,
            'total_snapshots': self.total_snapshots,
            'timemap_count': self.timemap_count,
            'first_snapshot': self.first_snapshot.isoformat() if self.first_snapshot else None,
            'last_snapshot': self.last_snapshot.isoformat() if self.last_snapshot else None,
            'avg_interval_days': self.avg_interval_days,
            'max_gap_days': self.max_gap_days,
            'years_covered': self.years_covered,
            'snapshots_per_year': json.loads(self.snapshots_per_year) if self.snapshots_per_year else {},
            'unique_versions': self.unique_versions,
            'is_good': self.is_good,
            'recommended': self.recommended,
            'analysis_time_sec': self.analysis_time_sec,
            'thematic_analysis_result': json.loads(self.thematic_analysis_result) if self.thematic_analysis_result else {},
            'ai_category': self.ai_category,
            'ai_confidence': self.ai_confidence,
            'ai_description': self.ai_description,
            'seo_metrics': json.loads(self.seo_metrics) if self.seo_metrics else {},
            'assessment_score': self.assessment_score,
            'assessment_summary': self.assessment_summary,
            'is_selected': self.is_selected,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.String(36), db.ForeignKey('analysis_tasks.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    domains_data = db.Column(db.Text)  # JSON string with selected domains
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'domains_data': json.loads(self.domains_data) if self.domains_data else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_public': self.is_public
        }

