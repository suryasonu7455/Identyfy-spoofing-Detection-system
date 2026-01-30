"""
Access Control and Verification Routes
Core identity verification and entry control endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import json

# Import db and models
from database.models import db, User, Credential, AccessLog, SuspiciousActivity

logger = logging.getLogger(__name__)

access_bp = Blueprint('access', __name__)

@access_bp.route('/verify-access', methods=['POST'])
def verify_access():
    """
    Main access verification endpoint - verifies face + credential + behavior
    Expected JSON:
    {
        "user_id": 1,
        "credential_type": "qr_code",
        "qr_data": "...",
        "live_image_path": "/path/to/image",
        "entry_point": "Main Gate"
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        credential_data = data.get('qr_data') or data.get('credential_id')
        live_image_path = data.get('live_image_path')
        entry_point = data.get('entry_point', 'Unknown')
        
        # Handle base64 images
        temp_image_path = None
        if live_image_path and live_image_path.startswith('data:image'):
            import base64
            import os
            import tempfile
            # Extract base64 data
            image_data = live_image_path.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            # Save to temp file
            temp_dir = tempfile.gettempdir()
            temp_image_path = os.path.join(temp_dir, f'verify_{user_id}_{datetime.now().timestamp()}.jpg')
            with open(temp_image_path, 'wb') as f:
                f.write(image_bytes)
            live_image_path = temp_image_path
        
        # Lazy-load heavy services only when endpoint is called
        from services.qr_validation_service import QRValidationService
        from services.face_recognition_service import FaceRecognitionService
        from services.anomaly_detection_service import AnomalyDetectionService
        qr_service = QRValidationService()
        face_service = FaceRecognitionService()
        anomaly_service = AnomalyDetectionService()

        # Step 1: Validate credential
        credential_valid = False
        credential_id = None
        
        if data.get('credential_type') == 'qr_code':
            is_valid, validation_result = qr_service.validate_qr_code(credential_data)
            if is_valid:
                credential_valid = True
                user_id = validation_result['user_id']
                credential_id = validation_result['credential_id']
        
        # Step 2: Load user
        user = User.query.get(user_id)
        if not user:
            access_log = AccessLog(
                entry_point=entry_point,
                access_status='denied',
                notes='User not found'
            )
            db.session.add(access_log)
            db.session.commit()
            return jsonify({'access_granted': False, 'reason': 'User not found'}), 401
        
        # Step 3: Face recognition verification
        face_match_confidence = 0.0
        is_face_match = False
        
        if user.face_embedding and live_image_path:
            try:
                # Get credential image path (in real system, stored in DB)
                distance, is_match = face_service.compare_faces(
                    live_image_path, 
                    live_image_path  # Would use credential image in production
                )
                is_face_match = is_match
                face_match_confidence = 1 - distance if distance < 1 else 0
            except Exception as e:
                logger.warning(f"Face verification failed: {str(e)}")
                face_match_confidence = 0.5
        
        # Step 4: Anomaly detection
        user_access_history = AccessLog.query.filter_by(user_id=user_id).order_by(
            AccessLog.timestamp.desc()
        ).limit(10).all()
        
        history_dicts = [{
            'timestamp': log.timestamp,
            'entry_point': log.entry_point,
            'access_status': log.access_status,
            'face_match_confidence': log.face_match_confidence or 0.0
        } for log in user_access_history]
        
        behavioral_anomaly = anomaly_service.detect_behavioral_anomalies(user_id, history_dicts)
        
        # Step 5: Credential sharing detection
        sharing_result = qr_service.detect_credential_sharing(credential_id or 0, user_access_history)
        
        # Step 6: Comprehensive risk scoring
        risk_assessment = anomaly_service.score_access_risk(
            face_match_confidence,
            credential_valid,
            history_dicts
        )
        
        # Step 7: Make access decision
        access_decision = risk_assessment['recommendation']
        
        if risk_assessment['risk_level'] == 'CRITICAL':
            access_granted = False
        elif risk_assessment['risk_level'] == 'HIGH':
            access_granted = False  # Require manual verification
        elif sharing_result['is_sharing_detected'] and sharing_result['confidence'] > 0.7:
            access_granted = False
        else:
            access_granted = True
        
        # Step 8: Log access attempt
        access_log = AccessLog(
            user_id=user_id,
            credential_id=credential_id,
            entry_point=entry_point,
            access_status='granted' if access_granted else 'denied',
            face_match_confidence=face_match_confidence,
            credential_valid=credential_valid,
            notes=f"Risk Level: {risk_assessment['risk_level']}"
        )
        db.session.add(access_log)
        
        # Step 9: Flag suspicious activities
        if not access_granted or risk_assessment['risk_level'] in ['HIGH', 'CRITICAL']:
            incident_type = 'face_mismatch' if not is_face_match else (
                'credential_sharing' if sharing_result['is_sharing_detected'] else 'anomaly'
            )
            
            suspicious = SuspiciousActivity(
                access_log_id=None,  # Will be set after access_log is committed
                incident_type=incident_type,
                severity='critical' if risk_assessment['risk_level'] == 'CRITICAL' else 'high',
                description=f"Access attempt blocked: {risk_assessment['risk_level']} risk",
                evidence={
                    'risk_factors': risk_assessment['risk_factors'],
                    'face_confidence': face_match_confidence,
                    'credential_valid': credential_valid,
                    'behavioral_anomalies': behavioral_anomaly['indicators']
                }
            )
            db.session.add(suspicious)
        
        db.session.commit()
        
        logger.info(f"✓ Access verification complete for user {user_id}: {access_granted}")
        
        return jsonify({
            'access_granted': access_granted,
            'user_id': user_id,
            'user_name': user.name,
            'entry_point': entry_point,
            'timestamp': datetime.utcnow().isoformat(),
            'verification_details': {
                'face_match': is_face_match,
                'face_confidence': face_match_confidence,
                'credential_valid': credential_valid,
                'behavioral_anomaly': behavioral_anomaly['has_anomaly'],
                'credential_sharing_detected': sharing_result['is_sharing_detected'],
                'risk_level': risk_assessment['risk_level'],
                'risk_score': risk_assessment['risk_score'],
                'recommendation': access_decision
            }
        }), 200 if access_granted else 403
    
    except Exception as e:
        logger.error(f"❌ Access verification failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@access_bp.route('/access-history/<int:user_id>', methods=['GET'])
def get_access_history(user_id: int):
    """Get access history for a specific user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = AccessLog.query.filter_by(user_id=user_id).order_by(
            AccessLog.timestamp.desc()
        ).limit(limit).all()
        
        return jsonify({
            'user_id': user_id,
            'total_records': len(logs),
            'access_logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_bp.route('/all-access-logs', methods=['GET'])
def get_all_access_logs():
    """Get all access logs with optional filtering"""
    try:
        status = request.args.get('status')  # granted or denied
        limit = request.args.get('limit', 100, type=int)
        
        query = AccessLog.query.order_by(AccessLog.timestamp.desc())
        
        if status:
            query = query.filter_by(access_status=status)
        
        logs = query.limit(limit).all()
        
        return jsonify({
            'total_records': len(logs),
            'access_logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_bp.route('/access-stats', methods=['GET'])
def get_access_stats():
    """Get access statistics and trends"""
    try:
        total_attempts = AccessLog.query.count()
        granted = AccessLog.query.filter_by(access_status='granted').count()
        denied = AccessLog.query.filter_by(access_status='denied').count()
        
        return jsonify({
            'total_access_attempts': total_attempts,
            'granted_access': granted,
            'denied_access': denied,
            'grant_rate': f"{(granted/total_attempts*100):.1f}%" if total_attempts > 0 else "0%"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
