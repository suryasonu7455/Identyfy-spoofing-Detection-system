import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson.objectid import ObjectId

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
client = MongoClient(MONGODB_URI)
db = client['identity_spoofing_db']

# Collections
users_collection = db['users']
verifications_collection = db['verifications']
access_logs_collection = db['access_logs']

# Create indexes
users_collection.create_index('email', unique=True)
users_collection.create_index('phone')
users_collection.create_index('unit')
verifications_collection.create_index('user_id')
verifications_collection.create_index('timestamp')
access_logs_collection.create_index('user_id')
access_logs_collection.create_index('timestamp')

class User:
    """User model for MongoDB"""

    @staticmethod
    def create(name, email, phone, unit, proof_type, face_embedding, enrollment_date=None):
        """Create a new user"""
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'unit': unit,
            'proof_type': proof_type,
            'face_embedding': face_embedding,  # List of floats for face vectors
            'enrollment_date': enrollment_date or datetime.now(),
            'status': 'active',
            'last_access': None,
            'access_count': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        try:
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            return user_data
        except DuplicateKeyError:
            raise ValueError(f"Email '{email}' already exists")

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            return users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return users_collection.find_one({'email': email})

    @staticmethod
    def get_by_phone(phone):
        """Get user by phone"""
        return users_collection.find_one({'phone': phone})

    @staticmethod
    def get_all(limit=100, skip=0):
        """Get all users with pagination"""
        return list(users_collection.find().limit(limit).skip(skip))

    @staticmethod
    def search(query):
        """Search users by name or email"""
        from pymongo import ASCENDING
        query_lower = query.lower()
        return list(users_collection.find({
            '$or': [
                {'name': {'$regex': query_lower, '$options': 'i'}},
                {'email': {'$regex': query_lower, '$options': 'i'}},
                {'phone': {'$regex': query_lower, '$options': 'i'}}
            ]
        }).sort('enrollment_date', ASCENDING))

    @staticmethod
    def update(user_id, updates):
        """Update user information"""
        try:
            updates['updated_at'] = datetime.now()
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except:
            return False

    @staticmethod
    def update_last_access(user_id):
        """Update last access time and increment access count"""
        try:
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {'last_access': datetime.now()},
                    '$inc': {'access_count': 1}
                }
            )
        except:
            pass

    @staticmethod
    def update_status(user_id, status):
        """Update user status (active, inactive, locked)"""
        return User.update(user_id, {'status': status})

    @staticmethod
    def delete(user_id):
        """Delete a user"""
        try:
            users_collection.delete_one({'_id': ObjectId(user_id)})
            # Also delete their verification records
            verifications_collection.delete_many({'user_id': user_id})
            return True
        except:
            return False

    @staticmethod
    def get_stats():
        """Get user statistics"""
        return {
            'total_users': users_collection.count_documents({}),
            'active_users': users_collection.count_documents({'status': 'active'}),
            'total_access_attempts': access_logs_collection.count_documents({}),
            'verified_count': access_logs_collection.count_documents({'status': 'approved'})
        }


class Verification:
    """Verification log model for MongoDB"""

    @staticmethod
    def log(user_id, match, confidence, status='pending', notes=None):
        """Log a verification attempt"""
        verification_data = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'timestamp': datetime.now(),
            'match': match,
            'confidence': confidence,
            'status': status,
            'notes': notes or '',
            'created_at': datetime.now()
        }

        result = verifications_collection.insert_one(verification_data)
        verification_data['_id'] = result.inserted_id
        return verification_data

    @staticmethod
    def get_by_id(verification_id):
        """Get verification record by ID"""
        try:
            return verifications_collection.find_one({'_id': ObjectId(verification_id)})
        except:
            return None

    @staticmethod
    def get_user_history(user_id, limit=50):
        """Get verification history for a user"""
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            from pymongo import DESCENDING
            return list(verifications_collection.find(
                {'user_id': user_obj_id}
            ).sort('timestamp', DESCENDING).limit(limit))
        except:
            return []

    @staticmethod
    def update_status(verification_id, status, notes=None):
        """Update verification status (pending, approved, denied)"""
        try:
            update_data = {'status': status}
            if notes:
                update_data['notes'] = notes
            update_data['updated_at'] = datetime.now()

            verifications_collection.update_one(
                {'_id': ObjectId(verification_id)},
                {'$set': update_data}
            )

            return Verification.get_by_id(verification_id)
        except:
            return None

    @staticmethod
    def get_stats_for_period(user_id, days=30):
        """Get verification statistics for a user in the last N days"""
        from datetime import timedelta
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            start_date = datetime.now() - timedelta(days=days)

            records = list(verifications_collection.find({
                'user_id': user_obj_id,
                'timestamp': {'$gte': start_date}
            }))

            if not records:
                return {
                    'total': 0,
                    'approved': 0,
                    'denied': 0,
                    'pending': 0,
                    'success_rate': 0
                }

            total = len(records)
            approved = len([r for r in records if r['status'] == 'approved'])
            denied = len([r for r in records if r['status'] == 'denied'])
            pending = len([r for r in records if r['status'] == 'pending'])
            success_rate = (approved / total * 100) if total > 0 else 0

            return {
                'total': total,
                'approved': approved,
                'denied': denied,
                'pending': pending,
                'success_rate': round(success_rate, 2)
            }
        except:
            return None


class AccessLog:
    """Access log model for MongoDB"""

    @staticmethod
    def log(user_id, action, result, details=None):
        """Log an access event"""
        log_data = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'timestamp': datetime.now(),
            'action': action,  # 'access_attempt', 'enrollment', 'verification', etc.
            'result': result,  # 'success', 'failed', 'pending'
            'details': details or {},
            'ip_address': None,
            'created_at': datetime.now()
        }

        result = access_logs_collection.insert_one(log_data)
        log_data['_id'] = result.inserted_id
        return log_data

    @staticmethod
    def get_user_logs(user_id, limit=100):
        """Get access logs for a user"""
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            from pymongo import DESCENDING
            return list(access_logs_collection.find(
                {'user_id': user_obj_id}
            ).sort('timestamp', DESCENDING).limit(limit))
        except:
            return []

    @staticmethod
    def get_recent_logs(limit=100):
        """Get recent access logs"""
        from pymongo import DESCENDING
        return list(access_logs_collection.find().sort('timestamp', DESCENDING).limit(limit))

    @staticmethod
    def get_stats():
        """Get access log statistics"""
        return {
            'total_logs': access_logs_collection.count_documents({}),
            'successful': access_logs_collection.count_documents({'result': 'success'}),
            'failed': access_logs_collection.count_documents({'result': 'failed'}),
            'pending': access_logs_collection.count_documents({'result': 'pending'})
        }
