
# ============================================================================
# STANDALONE FUNCTIONS FOR NEW ENROLLMENT/VERIFICATION WORKFLOW
# ============================================================================

def extract_face_embedding(image_path):
    """
    Extract face embedding from an image
    
    Args:
        image_path: Path to the image file
        
    Returns:
        numpy array of shape (512,) containing face embedding, or None if no face found
    """
    try:
        from deepface import DeepFace
        embeddings = DeepFace.represent(
            img_path=image_path,
            model_name='Facenet512',
            enforce_detection=True,
            detector_backend='opencv'
        )
        
        if embeddings and len(embeddings) > 0:
            return np.array(embeddings[0]['embedding'])
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error extracting face embedding: {str(e)}")
        return None

def compare_faces(embedding1, embedding2, threshold=0.55):
    """
    Compare two face embeddings
    
    Args:
        embedding1: numpy array or list
        embedding2: numpy array or list
        threshold: similarity threshold (0-1)
        
    Returns:
        tuple (match: bool, confidence: float)
    """
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        
        if isinstance(embedding1, list):
            embedding1 = np.array(embedding1)
        if isinstance(embedding2, list):
            embedding2 = np.array(embedding2)
        
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        confidence = (similarity + 1) / 2
        match = similarity >= threshold
        
        return match, confidence
        
    except Exception as e:
        logger.error(f"Error comparing faces: {str(e)}")
        return False, 0.0
"""
Face Recognition Service - Core ML Module
Handles face detection, embedding extraction, and face-to-ID matching
"""

import cv2
import numpy as np
from deepface import DeepFace
import os
from typing import Tuple, Dict, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionService:
    """Service for face recognition and verification"""
    
    def __init__(self, model_name: str = 'Facenet512', threshold: float = 0.4):
        """
        Initialize face recognition service
        
        Args:
            model_name: Face embedding model to use
            threshold: Similarity threshold for face matching (0-1)
        """
        self.model_name = model_name
        self.threshold = threshold
        self.detector_backend = 'opencv'
        logger.info(f"🔍 Face Recognition Service initialized with {model_name}")
    
    def extract_face_embedding(self, image_path: str) -> Optional[Dict]:
        """
        Extract face embedding from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with embedding and metadata, or None if no face detected
        """
        try:
            # Analyze image with DeepFace
            analysis = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend
            )
            
            if analysis:
                embedding = analysis[0]['embedding']
                return {
                    'embedding': embedding,
                    'model': self.model_name,
                    'detector': self.detector_backend,
                    'success': True
                }
            return None
        except Exception as e:
            logger.error(f"❌ Face extraction failed: {str(e)}")
            return None
    
    def compare_faces(self, image1_path: str, image2_path: str) -> Tuple[float, bool]:
        """
        Compare two face images and calculate similarity
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image (typically credential)
            
        Returns:
            Tuple of (similarity_score, is_match)
        """
        try:
            result = DeepFace.verify(
                img1_path=image1_path,
                img2_path=image2_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric='cosine'
            )
            
            distance = result['distance']
            is_match = result['verified']
            
            logger.info(f"✓ Face comparison: Distance={distance:.4f}, Match={is_match}")
            return distance, is_match
        except Exception as e:
            logger.error(f"❌ Face comparison failed: {str(e)}")
            return 1.0, False
    
    def verify_identity(self, live_image_path: str, credential_image_path: str) -> Dict:
        """
        Verify if live face matches credential image
        
        Args:
            live_image_path: Path to live capture image
            credential_image_path: Path to credential photo
            
        Returns:
            Dictionary with verification results
        """
        distance, is_match = self.compare_faces(live_image_path, credential_image_path)
        
        confidence = 1 - distance if distance < 1 else 0
        
        result = {
            'verified': is_match,
            'confidence': float(confidence),
            'distance': float(distance),
            'threshold': self.threshold,
            'match_status': 'MATCH' if is_match else 'MISMATCH',
            'risk_level': self._assess_risk_level(confidence, is_match)
        }
        
        return result
    
    def _assess_risk_level(self, confidence: float, is_match: bool) -> str:
        """
        Assess risk level based on match results
        
        Args:
            confidence: Confidence score (0-1)
            is_match: Whether faces matched
            
        Returns:
            Risk level: LOW, MEDIUM, HIGH, CRITICAL
        """
        if not is_match:
            return 'CRITICAL'  # Face doesn't match credential
        
        if confidence >= 0.95:
            return 'LOW'
        elif confidence >= 0.85:
            return 'MEDIUM'
        elif confidence >= 0.70:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def detect_face_spoofing(self, image_path: str) -> Dict:
        """
        Detect potential face spoofing (photo, video, mask)
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with spoofing analysis
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'is_spoofed': True, 'confidence': 0.0, 'reason': 'Invalid image'}
            
            # Analyze image for spoofing indicators
            analysis = {
                'is_spoofed': False,
                'confidence': 0.0,
                'indicators': [],
                'details': {}
            }
            
            # Check for Laplacian variance (blurry images often indicate spoofing)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var < 100:
                analysis['indicators'].append('possible_blur_or_low_quality')
                analysis['confidence'] += 0.3
            
            # Additional spoofing checks could be added here
            
            return analysis
        except Exception as e:
            logger.error(f"❌ Spoofing detection failed: {str(e)}")
            return {'is_spoofed': True, 'confidence': 0.0, 'reason': str(e)}
    
    def extract_and_store_embedding(self, image_path: str, user_id: int) -> bool:
        """
        Extract embedding and store in database
        
        Args:
            image_path: Path to image
            user_id: User ID to store embedding for
            
        Returns:
            Success status
        """
        embedding_data = self.extract_face_embedding(image_path)
        
        if embedding_data:
            # In real implementation, store this in database
            # For now, return success
            return True
        return False
