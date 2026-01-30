                                                                                                                                                                                                                                                                                                                        """
Authentication and User Management Routes
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
import json

# Import db and models
from database.models import db, User, Credential, AccessLog, SuspiciousActivity

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register-user', methods=['POST'])
def register_user():
    """
    Register a new resident/user with face enrollment
    Expected JSON:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "unit": "A101",
        "resident_type": "resident",
        "id_number": "DL12345678"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'unit']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User already exists with this email'}), 409
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            unit=data['unit'],
            resident_type=data.get('resident_type', 'resident'),
            id_number=data.get('id_number')
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"✓ User registered: {user.name} (ID: {user.id})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Registration failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/enroll-face/<int:user_id>', methods=['POST'])
def enroll_face(user_id: int):
    """
    Enroll user's face for identity verification
    Expects: image file upload as 'face_image'
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'face_image' not in request.files:
            return jsonify({'error': 'Face image not provided'}), 400
        
        file = request.files['face_image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        import os
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'{user_id}_face.jpg')
        file.save(temp_path)
        
        # Extract face embedding (lazy-load service to avoid heavy import at startup)
        from services.face_recognition_service import FaceRecognitionService
        face_service = FaceRecognitionService()
        embedding_data = face_service.extract_face_embedding(temp_path)
        
        if not embedding_data:
            return jsonify({'error': 'No face detected in image'}), 400
        
        # Store embedding in user record
        import json
        user.face_embedding = json.dumps(embedding_data['embedding'])
        db.session.commit()
        
        logger.info(f"✓ Face enrolled for user {user_id}")
        
        return jsonify({
            'message': 'Face enrolled successfully',
            'user_id': user_id,
            'embedding_model': embedding_data['model']
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Face enrollment failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/issue-credential/<int:user_id>', methods=['POST'])
def issue_credential(user_id: int):
    """
    Issue access credential (QR code, ID card pass)
    Expected JSON:
    {
        "credential_type": "qr_code",
        "valid_for_days": 30
    }
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        credential_type = data.get('credential_type', 'qr_code')
        valid_days = data.get('valid_for_days', 30)
        
        expires_at = datetime.utcnow() + timedelta(days=valid_days)
        
        # Generate QR code if applicable
        if credential_type == 'qr_code':
            credential = Credential(
                user_id=user_id,
                credential_type='qr_code',
                expires_at=expires_at
            )
            db.session.add(credential)
            db.session.flush()  # Get credential ID
            
            # Generate QR code
            from services.qr_validation_service import QRValidationService
            qr_service = QRValidationService()
            qr_result = qr_service.generate_qr_code(user_id, credential.id, expires_at)
            credential.qr_code_data = qr_result['qr_data']
            credential.credential_hash = qr_service.compute_qr_hash(qr_result['qr_data'])
        else:
            credential = Credential(
                user_id=user_id,
                credential_type=credential_type,
                expires_at=expires_at,
                credential_hash=f'{credential_type}_{user_id}_{datetime.utcnow().timestamp()}'
            )
            db.session.add(credential)
        
        db.session.commit()
        
        logger.info(f"✓ Credential issued to user {user_id}: {credential_type}")
        
        return jsonify({
            'message': 'Credential issued successfully',
            'credential_id': credential.id,
            'credential_type': credential_type,
            'valid_until': expires_at.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Credential issuance failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/list-users', methods=['GET'])
def list_users():
    """Get list of all registered users"""
    try:
        users = User.query.filter_by(is_active=True).all()
        return jsonify({
            'total': len(users),
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Get specific user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        credentials = Credential.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'user': user.to_dict(),
            'credentials': [c.to_dict() for c in credentials]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
