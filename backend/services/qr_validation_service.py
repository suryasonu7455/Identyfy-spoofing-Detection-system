"""
QR Code Validation Service
Handles QR code generation, validation, anti-cloning, and credential sharing detection
"""

import qrcode
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
from cryptography.fernet import Fernet
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRValidationService:
    """Service for QR code validation and anti-cloning"""
    
    def __init__(self, secret_key: str = os.getenv('QR_ENCODING_KEY', 'default-secret')):
        """
        Initialize QR validation service
        
        Args:
            secret_key: Secret key for encryption
        """
        self.secret_key = secret_key.encode()
        self.expiry_hours = int(os.getenv('QR_EXPIRY_HOURS', 24))
        logger.info("🔐 QR Validation Service initialized")
    
    def generate_qr_code(self, user_id: int, credential_id: int, 
                        valid_until: Optional[datetime] = None) -> Dict:
        """
        Generate secure QR code with anti-cloning features
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            valid_until: Expiry timestamp
            
        Returns:
            Dictionary with QR code data and metadata
        """
        if valid_until is None:
            valid_until = datetime.utcnow() + timedelta(hours=self.expiry_hours)
        
        # Create QR data payload
        qr_payload = {
            'user_id': user_id,
            'credential_id': credential_id,
            'issued_at': datetime.utcnow().isoformat(),
            'valid_until': valid_until.isoformat(),
            'nonce': hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        }
        
        # Generate HMAC signature for integrity verification
        payload_str = json.dumps(qr_payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key,
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Create final QR data
        qr_data = {
            'payload': qr_payload,
            'signature': signature
        }
        
        qr_json = json.dumps(qr_data)
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        logger.info(f"✓ QR code generated for user {user_id}")
        
        return {
            'qr_data': qr_json,
            'qr_image': qr_image,
            'user_id': user_id,
            'valid_until': valid_until.isoformat(),
            'nonce': qr_payload['nonce']
        }
    
    def validate_qr_code(self, qr_data: str) -> Tuple[bool, Dict]:
        """
        Validate QR code and check for tampering
        
        Args:
            qr_data: QR code data string
            
        Returns:
            Tuple of (is_valid, validation_result)
        """
        try:
            qr_json = json.loads(qr_data)
            payload = qr_json.get('payload', {})
            signature = qr_json.get('signature', '')
            
            # Verify signature
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.secret_key,
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, {
                    'valid': False,
                    'reason': 'SIGNATURE_MISMATCH',
                    'error': 'QR code has been tampered with'
                }
            
            # Check expiry
            valid_until = datetime.fromisoformat(payload.get('valid_until'))
            if datetime.utcnow() > valid_until:
                return False, {
                    'valid': False,
                    'reason': 'EXPIRED',
                    'error': 'QR code has expired'
                }
            
            return True, {
                'valid': True,
                'user_id': payload.get('user_id'),
                'credential_id': payload.get('credential_id'),
                'nonce': payload.get('nonce'),
                'issued_at': payload.get('issued_at'),
                'valid_until': payload.get('valid_until')
            }
        except Exception as e:
            logger.error(f"❌ QR validation failed: {str(e)}")
            return False, {
                'valid': False,
                'reason': 'INVALID_FORMAT',
                'error': str(e)
            }
    
    def detect_credential_sharing(self, credential_id: int, 
                                 access_logs: list) -> Dict:
        """
        Detect credential sharing by analyzing usage patterns
        
        Args:
            credential_id: Credential ID
            access_logs: List of recent access logs for this credential
            
        Returns:
            Dictionary with sharing detection results
        """
        if len(access_logs) < 2:
            return {'is_sharing_detected': False, 'confidence': 0.0}
        
        # Sort by timestamp
        sorted_logs = sorted(access_logs, key=lambda x: x.timestamp)
        
        suspicious_indicators = []
        
        # Check for impossible time gaps (same credential used in different locations)
        for i in range(len(sorted_logs) - 1):
            log1 = sorted_logs[i]
            log2 = sorted_logs[i + 1]
            
            time_diff = (log2.timestamp - log1.timestamp).total_seconds() / 60
            
            # If same credential used at different locations within 5 minutes
            if (log1.last_used_location != log2.last_used_location and 
                time_diff < 5):
                suspicious_indicators.append({
                    'type': 'IMPOSSIBLE_LOCATION_JUMP',
                    'time_gap_minutes': time_diff,
                    'location1': log1.last_used_location,
                    'location2': log2.last_used_location
                })
        
        # Check for unusual frequency
        if len(sorted_logs) > 5:
            time_span = (sorted_logs[-1].timestamp - sorted_logs[0].timestamp).total_seconds() / 3600
            frequency = len(sorted_logs) / time_span if time_span > 0 else 0
            
            if frequency > 10:  # More than 10 uses per hour
                suspicious_indicators.append({
                    'type': 'UNUSUAL_FREQUENCY',
                    'uses_per_hour': frequency
                })
        
        sharing_confidence = min(len(suspicious_indicators) * 0.3, 1.0)
        
        return {
            'is_sharing_detected': sharing_confidence > 0.5,
            'confidence': sharing_confidence,
            'suspicious_indicators': suspicious_indicators,
            'recommendation': 'BLOCK' if sharing_confidence > 0.7 else 'VERIFY'
        }
    
    def compute_qr_hash(self, qr_data: str) -> str:
        """
        Compute hash of QR code for deduplication
        
        Args:
            qr_data: QR code data
            
        Returns:
            Hash string
        """
        return hashlib.sha256(qr_data.encode()).hexdigest()
