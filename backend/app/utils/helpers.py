# app/utils/helpers.py
import uuid
import hashlib
from datetime import datetime
from typing import List


def generate_session_id() -> str:
    """Generate a unique session ID for anonymous users."""
    return str(uuid.uuid4())


def generate_pair_key(drug1_rxcui: str, drug2_rxcui: str) -> str:
    """
    Generate a consistent cache key for a drug pair.
    Order-independent — key is same regardless of drug order.
    """
    sorted_pair = sorted([drug1_rxcui, drug2_rxcui])
    raw = f"{sorted_pair[0]}_{sorted_pair[1]}"
    return hashlib.md5(raw.encode()).hexdigest()


def sanitize_drug_name(name: str) -> str:
    """Clean and sanitize a drug name input."""
    if not name:
        return ""
    # Strip whitespace, limit length, remove special chars
    cleaned = name.strip()[:100]
    # Allow only alphanumeric, spaces, hyphens, parentheses
    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789 -().,"
    )
    return "".join(c for c in cleaned if c in allowed)


def format_timestamp(dt: datetime = None) -> str:
    """Format a datetime to ISO 8601 string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def chunk_list(lst: List, size: int) -> List[List]:
    """Split a list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]