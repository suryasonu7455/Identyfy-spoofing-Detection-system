"""
Anomaly Detection Service
Detects unusual access patterns and behavioral anomalies
"""

from datetime import datetime, timedelta
from typing import Dict, List
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    """Service for detecting anomalous access patterns"""
    
    def __init__(self, threshold: float = 0.7):
        """
        Initialize anomaly detection service
        
        Args:
            threshold: Anomaly threshold (0-1)
        """
        self.threshold = threshold
        logger.info("🔍 Anomaly Detection Service initialized")
    
    def detect_behavioral_anomalies(self, user_id: int, 
                                   access_history: List[Dict]) -> Dict:
        """
        Detect unusual access patterns for a user
        
        Args:
            user_id: User ID
            access_history: List of recent access events
            
        Returns:
            Dictionary with anomaly scores and indicators
        """
        if len(access_history) < 3:
            return {
                'has_anomaly': False,
                'confidence': 0.0,
                'reason': 'Insufficient history'
            }
        
        anomaly_score = 0.0
        indicators = []
        
        # Check 1: Unusual time access
        hours = [access['timestamp'].hour for access in access_history]
        hour_counts = Counter(hours)
        
        # If accessing at unusual hours
        unusual_hours = [h for h in hours if h < 6 or h > 22]
        if len(unusual_hours) > len(hours) * 0.3:
            anomaly_score += 0.25
            indicators.append('UNUSUAL_TIME_ACCESS')
        
        # Check 2: Rapid successive accesses
        sorted_access = sorted(access_history, key=lambda x: x['timestamp'])
        for i in range(len(sorted_access) - 1):
            time_diff = (sorted_access[i+1]['timestamp'] - sorted_access[i]['timestamp']).total_seconds() / 60
            if time_diff < 2:  # Less than 2 minutes
                anomaly_score += 0.2
                indicators.append('RAPID_SUCCESSIVE_ACCESS')
                break
        
        # Check 3: Multiple entry points in short time
        locations = [access['entry_point'] for access in access_history[-10:]]
        unique_locations = len(set(locations))
        if unique_locations > 3:
            anomaly_score += 0.2
            indicators.append('MULTIPLE_ENTRY_POINTS')
        
        # Check 4: Access denial pattern changes
        denials = [a for a in access_history if a.get('access_status') == 'denied']
        if len(denials) > len(access_history) * 0.4:
            anomaly_score += 0.25
            indicators.append('HIGH_DENIAL_RATE')
        
        # Check 5: Confidence score drops
        recent_confidences = [a.get('face_match_confidence', 1.0) for a in access_history[-5:]]
        avg_confidence = sum(recent_confidences) / len(recent_confidences) if recent_confidences else 1.0
        if avg_confidence < 0.7:
            anomaly_score += 0.3
            indicators.append('LOW_FACE_CONFIDENCE')
        
        anomaly_score = min(anomaly_score, 1.0)  # Cap at 1.0
        
        return {
            'has_anomaly': anomaly_score > self.threshold,
            'confidence': anomaly_score,
            'indicators': indicators,
            'recommendation': 'MANUAL_REVIEW' if anomaly_score > 0.7 else 'AUTO_GRANT'
        }
    
    def detect_group_anomalies(self, access_logs: List[Dict]) -> Dict:
        """
        Detect anomalies in group access patterns (unauthorized group entry)
        
        Args:
            access_logs: List of recent access logs
            
        Returns:
            Dictionary with group anomaly analysis
        """
        # Group by timestamp and location
        time_location_groups = {}
        
        for log in access_logs:
            timestamp = log['timestamp']
            # Round to nearest minute
            minute_key = timestamp.replace(second=0, microsecond=0)
            location = log['entry_point']
            key = (minute_key, location)
            
            if key not in time_location_groups:
                time_location_groups[key] = []
            time_location_groups[key].append(log)
        
        suspicious_groups = []
        
        for (minute, location), logs in time_location_groups.items():
            if len(logs) >= 3:  # 3 or more people entering at same time/location
                authorized_count = sum(1 for log in logs if log.get('access_status') == 'granted')
                
                if authorized_count >= 1 and len(logs) > authorized_count:
                    suspicious_groups.append({
                        'timestamp': minute.isoformat(),
                        'location': location,
                        'total_entries': len(logs),
                        'authorized_entries': authorized_count,
                        'suspicious_entries': len(logs) - authorized_count,
                        'risk_level': 'HIGH' if len(logs) >= 5 else 'MEDIUM'
                    })
        
        return {
            'has_group_anomalies': len(suspicious_groups) > 0,
            'suspicious_groups': suspicious_groups,
            'total_suspicious': len(suspicious_groups)
        }
    
    def score_access_risk(self, face_confidence: float, 
                         credential_valid: bool,
                         user_history: List[Dict]) -> Dict:
        """
        Compute overall risk score for an access attempt
        
        Args:
            face_confidence: Face matching confidence (0-1)
            credential_valid: Whether credential is valid
            user_history: User's access history
            
        Returns:
            Dictionary with risk assessment
        """
        risk_score = 0.0
        risk_factors = []
        
        # Face confidence factor
        if face_confidence < 0.6:
            risk_score += 0.4
            risk_factors.append(f'LOW_FACE_CONFIDENCE ({face_confidence:.2f})')
        elif face_confidence < 0.8:
            risk_score += 0.2
            risk_factors.append(f'MEDIUM_FACE_CONFIDENCE ({face_confidence:.2f})')
        
        # Credential validity factor
        if not credential_valid:
            risk_score += 0.5
            risk_factors.append('INVALID_CREDENTIAL')
        
        # Behavioral anomaly factor
        if user_history:
            behavioral_anomaly = self.detect_behavioral_anomalies(0, user_history)
            if behavioral_anomaly['has_anomaly']:
                risk_score += behavioral_anomaly['confidence'] * 0.3
                risk_factors.extend(behavioral_anomaly['indicators'])
        
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'CRITICAL'
            recommendation = 'BLOCK'
        elif risk_score >= 0.6:
            risk_level = 'HIGH'
            recommendation = 'MANUAL_VERIFY'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
            recommendation = 'ALERT'
        else:
            risk_level = 'LOW'
            recommendation = 'GRANT'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'risk_factors': risk_factors
        }
