# app/services/cache_service.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.utils.helpers import generate_pair_key

logger = logging.getLogger(__name__)

# In-memory stats (resets on server restart)
_cache_stats = {
    "hits":    0,
    "misses":  0,
    "stores":  0,
    "errors":  0,
}


async def get_cached_interaction(
    rxcui1: Optional[str],
    rxcui2: Optional[str],
    drug1_name: str,
    drug2_name: str,
) -> Optional[Dict]:
    """
    Check MongoDB cache for a drug pair interaction.
    TTL handled automatically by MongoDB index.
    """
    global _cache_stats
    db = get_db()

    if db is None:
        logger.warning("Cache: DB not available")
        return None

    pair_key = _build_pair_key(
        rxcui1, rxcui2, drug1_name, drug2_name
    )

    try:
        cached = await db.drug_cache.find_one(
            {"pair_key": pair_key},
            # Only return needed fields
            {"_id": 0, "drug1": 1, "drug2": 1,
             "interaction_data": 1, "found": 1,
             "source": 1, "cached_at": 1}
        )

        if cached:
            _cache_stats["hits"] += 1
            age_hours = _get_age_hours(cached.get("cached_at"))
            logger.info(
                f"Cache HIT: '{drug1_name}' + '{drug2_name}' "
                f"(age: {age_hours:.1f}h)"
            )
            return {**cached, "from_cache": True}

        _cache_stats["misses"] += 1
        logger.info(
            f"Cache MISS: '{drug1_name}' + '{drug2_name}'"
        )
        return None

    except Exception as e:
        _cache_stats["errors"] += 1
        logger.error(f"Cache read error: {e}")
        return None


async def store_interaction_cache(
    rxcui1: Optional[str],
    rxcui2: Optional[str],
    drug1_name: str,
    drug2_name: str,
    interaction_data: Dict[str, Any],
    found: bool,
    source: str = "OpenFDA",
) -> bool:
    """Store interaction result in MongoDB cache."""
    global _cache_stats
    db = get_db()

    if db is None:
        return False

    pair_key = _build_pair_key(
        rxcui1, rxcui2, drug1_name, drug2_name
    )

    document = {
        "pair_key":         pair_key,
        "drug1":            drug1_name,
        "drug2":            drug2_name,
        "rxcui1":           rxcui1,
        "rxcui2":           rxcui2,
        "interaction_data": interaction_data,
        "found":            found,
        "source":           source,
        "cached_at":        datetime.utcnow(),
    }

    try:
        await db.drug_cache.update_one(
            {"pair_key": pair_key},
            {"$set": document},
            upsert=True,
        )
        _cache_stats["stores"] += 1
        logger.info(
            f"Cache STORE: '{drug1_name}' + '{drug2_name}' "
            f"(found={found})"
        )
        return True

    except Exception as e:
        _cache_stats["errors"] += 1
        logger.error(f"Cache write error: {e}")
        return False


async def get_cache_stats() -> Dict:
    """
    Return cache statistics including DB document count.
    Used by health check and admin monitoring.
    """
    global _cache_stats
    db  = get_db()
    doc_count = 0

    if db is not None:
        try:
            doc_count = await db.drug_cache.count_documents({})
        except Exception:
            pass

    total     = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate  = (
        round(_cache_stats["hits"] / total * 100, 1)
        if total > 0 else 0
    )

    return {
        "hits":       _cache_stats["hits"],
        "misses":     _cache_stats["misses"],
        "stores":     _cache_stats["stores"],
        "errors":     _cache_stats["errors"],
        "hit_rate":   f"{hit_rate}%",
        "total_cached_pairs": doc_count,
    }


async def clear_cache_for_pair(
    drug1_name: str,
    drug2_name: str,
) -> bool:
    """Remove a specific pair from cache."""
    db = get_db()
    if db is None:
        return False

    pair_key = _build_pair_key(
        None, None, drug1_name, drug2_name
    )

    try:
        result = await db.drug_cache.delete_one(
            {"pair_key": pair_key}
        )
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return False


async def clear_all_cache() -> int:
    """
    Clear entire cache. Use for testing only.
    Returns number of documents deleted.
    """
    db = get_db()
    if db is None:
        return 0

    try:
        result = await db.drug_cache.delete_many({})
        logger.warning(
            f"Cache CLEARED: {result.deleted_count} documents"
        )
        return result.deleted_count
    except Exception as e:
        logger.error(f"Cache clear all error: {e}")
        return 0


# ── Private helpers ───────────────────────────────────────────────────
def _build_pair_key(
    rxcui1: Optional[str],
    rxcui2: Optional[str],
    drug1_name: str,
    drug2_name: str,
) -> str:
    """Build order-independent cache key."""
    if rxcui1 and rxcui2:
        return generate_pair_key(rxcui1, rxcui2)

    # Fallback: use sorted drug names
    sorted_names = sorted([
        drug1_name.lower().strip(),
        drug2_name.lower().strip(),
    ])
    return generate_pair_key(sorted_names[0], sorted_names[1])


def _get_age_hours(cached_at: Optional[datetime]) -> float:
    """Calculate how old a cached entry is in hours."""
    if not cached_at:
        return 0.0
    delta = datetime.utcnow() - cached_at
    return delta.total_seconds() / 3600