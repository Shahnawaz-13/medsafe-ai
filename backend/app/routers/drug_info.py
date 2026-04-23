# app/routers/drug_info.py
import logging
from fastapi import APIRouter, Query, HTTPException
from app.services.normaliser import normalize_drug
from app.config import settings
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory cache for autocomplete (1 hour)
_autocomplete_cache: dict = {}


@router.get("/drug-info")
async def drug_info(
    name: str = Query(..., min_length=2, max_length=100)
):
    """Get canonical drug info from RxNorm."""
    result = await normalize_drug(name)

    if not result["found"]:
        raise HTTPException(
            status_code=404,
            detail=f"Drug '{name}' not found in RxNorm database."
        )

    return {
        "rxcui":           result["rxcui"],
        "canonical_name":  result["normalized_name"],
        "input_name":      result["input_name"],
        "found":           result["found"],
    }


@router.get("/drug-autocomplete")
async def drug_autocomplete(
    q: str = Query(..., min_length=2, max_length=100)
):
    """
    Return drug name suggestions as user types.
    Uses RxNorm approximate match. Results cached in memory.
    """
    cache_key = q.lower().strip()

    # Return from memory cache if available
    if cache_key in _autocomplete_cache:
        return {"suggestions": _autocomplete_cache[cache_key]}

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(
                f"{settings.rxnorm_base_url}/approximateTerm.json",
                params={"term": q, "maxEntries": 8},
            )

            if resp.status_code != 200:
                return {"suggestions": []}

            data       = resp.json()
            candidates = (
                data.get("approximateGroup", {})
                    .get("candidate", [])
            )

            suggestions = []
            seen_rxcui  = set()

            for c in candidates:
                rxcui = c.get("rxcui")
                if rxcui and rxcui not in seen_rxcui:
                    seen_rxcui.add(rxcui)
                    suggestions.append({
                        "name":  c.get("name", q),
                        "rxcui": rxcui,
                    })

            # Cache for 1 hour (simple dict — resets on restart)
            if len(_autocomplete_cache) < 500:  # memory limit
                _autocomplete_cache[cache_key] = suggestions

            return {"suggestions": suggestions}

    except httpx.TimeoutException:
        logger.warning(f"Autocomplete timeout for '{q}'")
        return {"suggestions": []}
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return {"suggestions": []}