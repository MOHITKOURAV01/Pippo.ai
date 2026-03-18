import json
import logging
import re
from typing import Any, Dict, Optional

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger("LegalAgent")

def parse_json_with_retry(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to extract and parse JSON from LLM output.
    Handles common issues like markdown blocks or leading/trailing text.
    """
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Look for JSON block in markdown
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Look for any curly brace block
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            logger.error(f"Failed to parse JSON even with regex: {e}")
            
    return None

def calculate_hybrid_score(llm_score: float, ml_score: float) -> float:
    """
    Calculates a weighted hybrid score.
    Weights: 60% LLM, 40% ML.
    """
    return round((0.6 * llm_score) + (0.4 * ml_score), 2)

def map_score_to_level(score: float) -> str:
    """ Maps numerical score (0-100) to qualitative risk level. """
    if score >= 80: return "Critical"
    if score >= 60: return "High"
    if score >= 40: return "Medium"
    if score >= 20: return "Low"
    return "Minimal"
