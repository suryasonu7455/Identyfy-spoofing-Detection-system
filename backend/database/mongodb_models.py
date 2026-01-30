"""
MongoDB Database Models
Stores user data with face embeddings and proof information
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB Connection
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'identity_spoofing_db')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    db = client[DB_NAME]
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"⚠️ MongoDB Connection Failed: {e}")
    print("Using local MongoDB - ensure mongod is running")
    db = None

# Collections
users_collection = None
enrollments_collection = None
verifications_collection = None

def init_db():
    """Initialize database collections"""
    global users_collection, enrollments_collection, verifications_collection
    
    try:
        users_collection = db['users']
        enrollments_collection = db['enrollments']
        verifications_collection = db['verifications']
        
        # Create indexes
        users_collection.create_index([('email', 1)], unique=True)
        users_collection.create_index([('user_id', 1)], unique=True)
        verifications_collection.create_index([('user_id', 1)])
        verifications_collection.create_index([('timestamp', -1)])
        
        print("✅ Database collections initialized")
    except Exception as e:
        print(f"Error initializing database: {e}")

class User:
    """User Model - Stores new user enrollment data"""
    
    @staticmethod
    def create(name, email, phone, unit, proof_type, face_embedding):
        """Create new user"""
        try:
            user_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'unit': unit,
                'proof_type': proof_type,  # ID, Passport, License, etc.
                'face_embedding': face_embedding,  # 128-D numpy array converted to list
                'status': 'active',
                'created_at': datetime.utcnow(),
                'enrollments': 1,
                'last_access': None
            }
            
            result = users_collection.insert_one(user_data)
            print(f"✅ User created: {result.inserted_id}")
            return {
                'success': True,
                'user_id': str(result.inserted_id),
                'message': f'User {name} enrolled successfully!'
            }
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        from bson import ObjectId
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            return user
        except:
            return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return users_collection.find_one({'email': email})
    
    @staticmethod
    def get_all():
        """Get all users"""
        return list(users_collection.find({}))
    
    @staticmethod
    def update_access(user_id):
        """Update last access time"""
        from bson import ObjectId
        try:
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {'last_access': datetime.utcnow()},
                    '$inc': {'total_accesses': 1}
                }
            )
        except Exception as e:
            print(f"Error updating access: {e}")

class Verification:
    """Verification Model - Logs each verification attempt"""
    
    @staticmethod
    def log(user_id, access_granted, reason, timestamp=None):
        """Log verification attempt"""
        try:
            verification_data = {
                'user_id': user_id,
                'access_granted': access_granted,
                'reason': reason,
                'timestamp': timestamp or datetime.utcnow(),
                'verified_by': 'system'
            }
            
            result = verifications_collection.insert_one(verification_data)
            return {'success': True, 'verification_id': str(result.inserted_id)}
        except Exception as e:
            print(f"Error logging verification: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_history(user_id, limit=20):
        """Get user's verification history"""
        try:
            history = list(verifications_collection
                          .find({'user_id': user_id})
                          .sort('timestamp', -1)
                          .limit(limit))
            return history
        except Exception as e:
            print(f"Error getting history: {e}")
            return []

# Initialize when module is imported
if db:
    init_db()
