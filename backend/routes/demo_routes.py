"""
Demo/Seed Routes to populate sample data for the dashboard
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

from database.models import db, User, Credential, AccessLog, SuspiciousActivity

demo_bp = Blueprint('demo', __name__)


@demo_bp.route('/seed', methods=['POST'])
def seed_demo():
    """Create demo users, credentials, access logs and incidents.

    Query params:
      fresh=true  -> clears existing records before seeding
    """
    fresh = request.args.get('fresh', 'false').lower() == 'true'

    if fresh:
        SuspiciousActivity.query.delete()
        AccessLog.query.delete()
        Credential.query.delete()
        User.query.delete()
        db.session.commit()

    # Create users
    users_data = [
        dict(name='Rahul Kumar', email='rahul@example.com', phone='9876543210', unit='A101', resident_type='resident', id_number='DL12345678'),
        dict(name='Priya Singh', email='priya@example.com', phone='9876500001', unit='B202', resident_type='resident', id_number='DL87654321'),
        dict(name='Security Staff', email='guard@example.com', phone='9000000001', unit='Gate', resident_type='staff', id_number='STAFF001'),
    ]

    users = []
    for u in users_data:
        user = User(
            name=u['name'], email=u['email'], phone=u['phone'], unit=u['unit'],
            resident_type=u['resident_type'], id_number=u['id_number'], is_active=True
        )
        db.session.add(user)
        users.append(user)
    db.session.flush()

    # Create credentials (simple hashes)
    creds = []
    for user in users:
        c = Credential(
            user_id=user.id,
            credential_type='qr_code',
            credential_hash=f"QR_{user.id}_{int(datetime.utcnow().timestamp())}",
            qr_code_data=f"QRDATA_{user.id}",
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.session.add(c)
        creds.append(c)
    db.session.flush()

    # Access logs across last 24h
    now = datetime.utcnow()
    entry_points = ['Main Gate', 'Side Gate', 'Parking']
    logs = []
    for hour_back in [20, 16, 12, 8, 4, 0]:
        ts = now - timedelta(hours=hour_back)
        for user in users:
            status = 'granted' if random.random() > 0.15 else 'denied'
            logs.append(AccessLog(
                user_id=user.id,
                credential_id=creds[users.index(user)].id,
                entry_point=random.choice(entry_points),
                timestamp=ts,
                access_status=status,
                face_match_confidence=round(random.uniform(0.6, 0.98), 2),
                credential_valid=True,
                notes='Demo log'
            ))
        # Add an extra denied attempt to generate incidents
        logs.append(AccessLog(
            user_id=users[0].id,
            credential_id=creds[0].id,
            entry_point='Side Gate',
            timestamp=ts + timedelta(minutes=5),
            access_status='denied',
            face_match_confidence=round(random.uniform(0.2, 0.5), 2),
            credential_valid=False,
            notes='Demo denied'
        ))

    db.session.bulk_save_objects(logs)
    db.session.flush()

    # Suspicious incidents for denied attempts
    incidents = []
    recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(8).all()
    for log in recent_logs:
        if log.access_status == 'denied':
            incidents.append(SuspiciousActivity(
                access_log_id=log.id,
                incident_type='anomaly',
                severity='high',
                description='Demo: high risk access attempt',
                detected_at=log.timestamp,
                status='open',
                evidence={
                    'risk_factors': ['multiple_denials', 'low_face_confidence'],
                    'face_confidence': log.face_match_confidence,
                    'credential_valid': log.credential_valid
                }
            ))

    if incidents:
        db.session.bulk_save_objects(incidents)

    db.session.commit()

    return jsonify({
        'message': 'Demo data seeded successfully',
        'users_created': len(users),
        'credentials_created': len(creds),
        'logs_created': len(logs),
        'incidents_created': len(incidents)
    }), 201


@demo_bp.route('/reset', methods=['POST'])
def reset_demo():
    """Clear all data (useful before reseeding)."""
    SuspiciousActivity.query.delete()
    AccessLog.query.delete()
    Credential.query.delete()
    User.query.delete()
    db.session.commit()
    return jsonify({'message': 'All data cleared'}), 200
