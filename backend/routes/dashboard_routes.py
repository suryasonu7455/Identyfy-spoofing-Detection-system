"""
Dashboard and Monitoring Routes
Provides real-time insights and analytics
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging

# Import db and models
from database.models import db, AccessLog, SuspiciousActivity, User

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """Get overall system status and key metrics"""
    try:
        # Get current stats
        total_users = User.query.filter_by(is_active=True).count()
        total_access_attempts = AccessLog.query.count()
        
        # Last 24 hours stats
        last_24h = datetime.utcnow() - timedelta(hours=24)
        attempts_24h = AccessLog.query.filter(AccessLog.timestamp >= last_24h).count()
        denied_24h = AccessLog.query.filter(
            AccessLog.timestamp >= last_24h,
            AccessLog.access_status == 'denied'
        ).count()
        
        # Suspicious activities
        open_incidents = SuspiciousActivity.query.filter_by(status='open').count()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'system_status': 'healthy',
            'statistics': {
                'total_users': total_users,
                'total_access_attempts': total_access_attempts,
                'attempts_24h': attempts_24h,
                'denied_24h': denied_24h,
                'denial_rate_24h': f"{(denied_24h/attempts_24h*100):.1f}%" if attempts_24h > 0 else "0%",
                'open_incidents': open_incidents
            }
        }), 200
    except Exception as e:
        logger.error(f"❌ Dashboard overview failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/incidents', methods=['GET'])
def get_incidents():
    """Get list of suspicious incidents"""
    try:
        status = request.args.get('status')  # open, investigating, resolved
        limit = request.args.get('limit', 50, type=int)
        
        query = SuspiciousActivity.query.order_by(SuspiciousActivity.detected_at.desc())
        
        if status:
            query = query.filter_by(status=status)
        
        incidents = query.limit(limit).all()
        
        return jsonify({
            'total_incidents': len(incidents),
            'incidents': [
                {
                    'id': inc.id,
                    'incident_type': inc.incident_type,
                    'severity': inc.severity,
                    'description': inc.description,
                    'detected_at': inc.detected_at.isoformat(),
                    'status': inc.status
                }
                for inc in incidents
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/incident/<int:incident_id>', methods=['GET'])
def get_incident_details(incident_id: int):
    """Get detailed information about a specific incident"""
    try:
        incident = SuspiciousActivity.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        access_log = AccessLog.query.get(incident.access_log_id)
        user = User.query.get(access_log.user_id) if access_log else None
        
        return jsonify({
            'incident': {
                'id': incident.id,
                'incident_type': incident.incident_type,
                'severity': incident.severity,
                'description': incident.description,
                'detected_at': incident.detected_at.isoformat(),
                'status': incident.status,
                'evidence': incident.evidence,
                'resolution_notes': incident.resolution_notes
            },
            'related_access': access_log.to_dict() if access_log else None,
            'user': user.to_dict() if user else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/high-risk-users', methods=['GET'])
def get_high_risk_users():
    """Identify users with suspicious access patterns"""
    try:
        # Find users with multiple denied attempts
        denied_attempts = db.session.query(
            AccessLog.user_id,
            db.func.count(AccessLog.id).label('denied_count')
        ).filter(
            AccessLog.access_status == 'denied'
        ).group_by(
            AccessLog.user_id
        ).order_by(
            db.func.count(AccessLog.id).desc()
        ).limit(10).all()
        
        high_risk_users = []
        for user_id, denied_count in denied_attempts:
            if denied_count >= 3:  # 3 or more denials
                user = User.query.get(user_id)
                if user:
                    high_risk_users.append({
                        'user_id': user.id,
                        'user_name': user.name,
                        'denied_attempts': denied_count,
                        'risk_level': 'CRITICAL' if denied_count >= 5 else 'HIGH'
                    })
        
        return jsonify({
            'total_high_risk_users': len(high_risk_users),
            'users': high_risk_users
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/activity-timeline', methods=['GET'])
def get_activity_timeline():
    """Get activity timeline for the last N hours"""
    try:
        hours = request.args.get('hours', 24, type=int)
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get hourly breakdown
        logs = AccessLog.query.filter(
            AccessLog.timestamp >= start_time
        ).order_by(AccessLog.timestamp.asc()).all()
        
        # Group by hour
        hourly_data = {}
        for log in logs:
            hour_key = log.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {'granted': 0, 'denied': 0}
            
            if log.access_status == 'granted':
                hourly_data[hour_key]['granted'] += 1
            else:
                hourly_data[hour_key]['denied'] += 1
        
        return jsonify({
            'time_range_hours': hours,
            'hourly_activity': hourly_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/entry-points', methods=['GET'])
def get_entry_points_stats():
    """Get statistics by entry point"""
    try:
        entry_points = db.session.query(
            AccessLog.entry_point,
            db.func.count(AccessLog.id).label('total'),
            db.func.sum(
                db.case(
                    (AccessLog.access_status == 'granted', 1),
                    else_=0
                )
            ).label('granted'),
            db.func.sum(
                db.case(
                    (AccessLog.access_status == 'denied', 1),
                    else_=0
                )
            ).label('denied')
        ).group_by(AccessLog.entry_point).all()
        
        stats = []
        for ep in entry_points:
            if ep.entry_point:
                stats.append({
                    'entry_point': ep.entry_point,
                    'total_attempts': ep.total,
                    'granted': ep.granted or 0,
                    'denied': ep.denied or 0
                })
        
        return jsonify({
            'entry_points': sorted(stats, key=lambda x: x['total_attempts'], reverse=True)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/incident-update/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id: int):
    """Update incident status and notes"""
    try:
        incident = SuspiciousActivity.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        data = request.get_json()
        
        if 'status' in data:
            incident.status = data['status']
        if 'resolution_notes' in data:
            incident.resolution_notes = data['resolution_notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Incident updated successfully',
            'incident_id': incident_id,
            'status': incident.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
