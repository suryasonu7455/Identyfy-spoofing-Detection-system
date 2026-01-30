from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from database.mongodb_models import User, Verification
from services.face_recognition_service import extract_face_embedding, compare_faces
import os
import tempfile
from datetime import datetime

enrollment_routes = Blueprint('enrollment', __name__, url_prefix='/api/enrollment')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@enrollment_routes.route('/enroll-new-user', methods=['POST'])
def enroll_new_user():
    """
    Enroll a new user with face capture
    Expects: name, email, phone, unit, proof_type, face_image (file)
    """
    try:
        if 'face_image' not in request.files:
            return jsonify({'success': False, 'error': 'No face image provided'}), 400

        file = request.files['face_image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Use PNG, JPG, JPEG, or GIF'}), 400

        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        unit = request.form.get('unit', '').strip()
        proof_type = request.form.get('proof_type', '').lower()

        if not all([name, email, phone, unit, proof_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered'}), 409

        # Save temp file and extract face embedding
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(temp_path)

        try:
            embedding = extract_face_embedding(temp_path)
            if embedding is None:
                return jsonify({'success': False, 'error': 'No face detected in image'}), 400

            # Create user in MongoDB
            user = User.create(
                name=name,
                email=email,
                phone=phone,
                unit=unit,
                proof_type=proof_type,
                face_embedding=embedding.tolist(),  # Convert numpy array to list
                enrollment_date=datetime.now()
            )

            return jsonify({
                'success': True,
                'message': f'Successfully enrolled {name}!',
                'user_id': str(user['_id']),
                'user': {
                    'id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email']
                }
            }), 201

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enrollment_routes.route('/verify-user', methods=['POST'])
def verify_user():
    """
    Verify a user's face during access attempt
    Expects: user_id, face_image (file)
    """
    try:
        if 'face_image' not in request.files:
            return jsonify({'success': False, 'error': 'No face image provided'}), 400

        file = request.files['face_image']
        user_id = request.form.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400

        # Get user from MongoDB
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Save temp file and extract face embedding
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(temp_path)

        try:
            # Extract embedding from verification image
            verification_embedding = extract_face_embedding(temp_path)
            if verification_embedding is None:
                return jsonify({'success': False, 'error': 'No face detected in image'}), 400

            # Compare faces
            stored_embedding = user['face_embedding']
            match, confidence = compare_faces(verification_embedding, stored_embedding)

            # Log verification attempt
            verification = Verification.log(
                user_id=user_id,
                match=match,
                confidence=float(confidence),
                status='pending'
            )

            return jsonify({
                'success': True,
                'match': match,
                'confidence': float(confidence),
                'verification_id': str(verification['_id']),
                'user': {
                    'id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email']
                }
            }), 200

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enrollment_routes.route('/search-users', methods=['GET'])
def search_users():
    """
    Search for users by name or email
    Query params: query
    """
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400

        users = User.search(query)
        return jsonify({
            'success': True,
            'users': [
                {
                    '_id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'unit': user['unit'],
                    'proof_type': user['proof_type'],
                    'status': user.get('status', 'active'),
                    'enrollment_date': user['enrollment_date'].isoformat() if 'enrollment_date' in user else None
                }
                for user in users
            ]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enrollment_routes.route('/grant-access', methods=['POST'])
def grant_access():
    """
    Grant access to a verified user
    Expects: user_id, verification_id, notes
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        verification_id = data.get('verification_id')
        notes = data.get('notes', 'Approved by security')

        if not user_id or not verification_id:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Update verification status
        verification = Verification.update_status(verification_id, 'approved', notes)

        # Update user last access
        User.update_last_access(user_id)

        return jsonify({
            'success': True,
            'message': 'Access granted',
            'verification_id': verification_id
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enrollment_routes.route('/deny-access', methods=['POST'])
def deny_access():
    """
    Deny access to a user
    Expects: user_id, verification_id, notes
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        verification_id = data.get('verification_id')
        notes = data.get('notes', 'Denied by security')

        if not user_id or not verification_id:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Update verification status
        verification = Verification.update_status(verification_id, 'denied', notes)

        return jsonify({
            'success': True,
            'message': 'Access denied',
            'verification_id': verification_id
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@enrollment_routes.route('/user-history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """
    Get verification history for a user
    """
    try:
        history = Verification.get_user_history(user_id)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'history': [
                {
                    'id': str(v['_id']),
                    'timestamp': v['timestamp'].isoformat(),
                    'match': v['match'],
                    'confidence': v['confidence'],
                    'status': v['status'],
                    'notes': v.get('notes', '')
                }
                for v in history
            ]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
