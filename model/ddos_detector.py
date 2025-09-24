import numpy as np
import tensorflow as tf
import logging
import os
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ddos_model.keras")

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("DDoS detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load DDoS detection model: {str(e)}")
    model = None

# Define the exact feature order as per your training data (77 features)
FEATURE_NAMES = [
    "Protocol", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Fwd Packets Length Total", "Bwd Packets Length Total", "Fwd Packet Length Max",
    # ... (all 77 features as shown in the dataset)
]

def extract_features_from_alert(alert_json: Dict[str, Any]) -> List[float]:
    """Extract DDoS detection features from alert JSON"""
    # Complete implementation as shown above
    # Maps alert metrics to the 77 required features
    
def predict_ddos(alert_json: Dict[str, Any]) -> tuple[float, bool]:
    """Predict DDoS probability from alert data"""
    # Returns (probability, is_detected)
