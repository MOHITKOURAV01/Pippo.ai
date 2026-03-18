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
