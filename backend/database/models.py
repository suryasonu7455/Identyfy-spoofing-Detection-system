"""
Database Models for Identity Spoofing Detection System
"""

from datetime import datetime, timedelta
import json
from flask_sqlalchemy import SQLAlchemy

# Create db instance here to avoid circular imports
db = SQLAlchemy()

try:
    from sqlalchemy.dialects.postgresql import JSON as JSONTYPE
except ImportError:
    # Fallback for SQLite
    JSONTYPE = None

class User(db.Model):
    """Resident/User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # Flat/House number
    resident_type = db.Column(db.String(50), default='resident')  # resident, visitor, vendor, staff
    face_embedding = db.Column(db.Text)  # Stored as JSON string
    id_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    credentials = db.relationship('Credential', backref='user', lazy=True, cascade='all, delete-orphan')
    access_logs = db.relationship('AccessLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'unit': self.unit,
            'resident_type': self.resident_type,
            'id_number': self.id_number,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class Credential(db.Model):
    """Access credentials (QR codes, ID cards, passes)"""
    __tablename__ = 'credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    credential_type = db.Column(db.String(50), nullable=False)  # qr_code, id_card, pass, rfid
    credential_hash = db.Column(db.String(255), unique=True, nullable=False)
    qr_code_data = db.Column(db.Text)  # Encrypted QR data
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)
    last_used_location = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Credential {self.credential_type} for User {self.user_id}>'
    
    def is_expired(self):
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'credential_type': self.credential_type,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }


class AccessLog(db.Model):
    """Log of all access attempts"""
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    credential_id = db.Column(db.Integer, db.ForeignKey('credentials.id'), nullable=True)
    entry_point = db.Column(db.String(100), nullable=False)
    access_status = db.Column(db.String(50), default='pending')  # pending, granted, denied
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    face_match_confidence = db.Column(db.Float)  # 0-1 confidence score
    credential_valid = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<AccessLog {self.timestamp} - {self.access_status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entry_point': self.entry_point,
            'access_status': self.access_status,
            'timestamp': self.timestamp.isoformat(),
            'face_match_confidence': self.face_match_confidence,
            'credential_valid': self.credential_valid,
            'notes': self.notes
        }


class SuspiciousActivity(db.Model if db else object):
    """Flagged suspicious activities and security incidents"""
    __tablename__ = 'suspicious_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    access_log_id = db.Column(db.Integer, db.ForeignKey('access_logs.id'), nullable=False)
    incident_type = db.Column(db.String(100), nullable=False)  # face_mismatch, credential_sharing, impersonation, anomaly
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    description = db.Column(db.Text)
    evidence = db.Column(JSONTYPE if JSONTYPE else db.Text)  # Store evidence data as JSON
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='open')  # open, investigating, resolved, false_positive
    resolution_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SuspiciousActivity {self.incident_type} - {self.severity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'access_log_id': self.access_log_id,
            'incident_type': self.incident_type,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'status': self.status
        }


class AuditTrail(db.Model):
    """Audit trail for compliance and transparency"""
    __tablename__ = 'audit_trail'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    performed_by = db.Column(db.String(100))  # Admin or system
    details = db.Column(JSONTYPE if JSONTYPE else db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditTrail {self.action} at {self.timestamp}>'
