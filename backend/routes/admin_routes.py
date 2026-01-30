from flask import Blueprint, request, jsonify
from database.models import User, AccessLog, db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users for admin panel"""
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'unit': user.unit,
                'role': user.role if hasattr(user, 'role') else 'resident',
                'status': user.status if hasattr(user, 'status') else 'active',
                'face_enrolled': user.face_embedding is not None,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
            })
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': len(users_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'unit' in data:
            user.unit = data['unit']
        if 'status' in data and hasattr(user, 'status'):
            user.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive system statistics"""
    try:
        # Total users
        total_users = User.query.count()
        
        # Users with face enrolled
        users_with_face = User.query.filter(User.face_embedding.isnot(None)).count()
        
        # Access logs today
        from datetime import date
        today = date.today()
        today_logs = AccessLog.query.filter(
            db.func.date(AccessLog.timestamp) == today
        ).count()
        
        # Successful access today
        successful_today = AccessLog.query.filter(
            db.func.date(AccessLog.timestamp) == today,
            AccessLog.access_granted == True
        ).count()
        
        # Failed access today
        failed_today = AccessLog.query.filter(
            db.func.date(AccessLog.timestamp) == today,
            AccessLog.access_granted == False
        ).count()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'users_with_face': users_with_face,
                'today_verifications': today_logs,
                'successful_today': successful_today,
                'failed_today': failed_today,
                'enrollment_rate': round((users_with_face / total_users * 100) if total_users > 0 else 0, 1),
                'success_rate': round((successful_today / today_logs * 100) if today_logs > 0 else 0, 1)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
