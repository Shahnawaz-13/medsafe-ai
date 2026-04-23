# app/routers/drug_info.py
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.services.normaliser import normalize_drug_name
from app.config import settings
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory cache for autocomplete
_autocomplete_cache: dict = {}
_drug_info_cache:    dict = {}

# Max cache size (resets on server restart)
MAX_CACHE_SIZE = 1000


@router.get("/drug-info")
async def drug_info(
    name: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Drug name to look up"
    )
):
    """
    Get canonical drug information from RxNorm.
    Returns rxcui, canonical name, and drug class.
    """
    name_clean = name.strip()

    # Check memory cache first
    cache_key = name_clean.lower()
    if cache_key in _drug_info_cache:
        logger.info(f"Drug info cache hit: '{name_clean}'")
        return _drug_info_cache[cache_key]

    # Normalize via RxNorm
    result = await normalize_drug_name(name_clean)

    if not result["found"]:
        raise HTTPException(
            status_code=404,
            detail={
                "error":   "Drug not found",
                "message": (
                    f"'{name_clean}' could not be found in "
                    f"RxNorm database. Check spelling or try "
                    f"the generic name."
                ),
                "suggestion": "Use /api/drug-autocomplete to search",
            }
        )

    # Get drug class from RxNorm
    drug_class = await _get_drug_class(result.get("rxcui"))

    response = {
        "rxcui":          result["rxcui"],
        "canonical_name": result["normalized_name"],
        "input_name":     result["input_name"],
        "drug_class":     drug_class,
        "found":          True,
        "source":         "RxNorm",
    }

    # Cache result
    if len(_drug_info_cache) < MAX_CACHE_SIZE:
        _drug_info_cache[cache_key] = response

    return response


@router.get("/drug-autocomplete")
async def drug_autocomplete(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Partial drug name to search"
    )
):
    """
    Return drug name suggestions as user types.
    Uses RxNorm approximate match — results cached in memory.
    """
    q_clean   = q.strip()
    cache_key = q_clean.lower()

    # Return from memory cache if available
    if cache_key in _autocomplete_cache:
        logger.debug(f"Autocomplete cache hit: '{q_clean}'")
        return {
            "suggestions": _autocomplete_cache[cache_key],
            "from_cache":  True,
        }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(
                f"{settings.rxnorm_base_url}/approximateTerm.json",
                params={
                    "term":       q_clean,
                    "maxEntries": 10,
                },
            )

            if resp.status_code != 200:
                logger.warning(
                    f"RxNorm autocomplete failed: "
                    f"status={resp.status_code}"
                )
                return {"suggestions": [], "from_cache": False}

            data       = resp.json()
            candidates = (
                data.get("approximateGroup", {})
                    .get("candidate", [])
            )

            # Deduplicate and format
            suggestions = []
            seen_rxcui  = set()
            seen_names  = set()

            for c in candidates:
                rxcui = c.get("rxcui")
                name  = c.get("name", "")

                # Skip duplicates
                if rxcui in seen_rxcui:
                    continue
                if name.lower() in seen_names:
                    continue

                seen_rxcui.add(rxcui)
                seen_names.add(name.lower())

                suggestions.append({
                    "name":  name,
                    "rxcui": rxcui,
                    "score": c.get("score", 0),
                })

                if len(suggestions) >= 8:
                    break

            # Sort by score descending
            suggestions.sort(
                key=lambda x: x.get("score", 0),
                reverse=True
            )

            # Cache result
            if len(_autocomplete_cache) < MAX_CACHE_SIZE:
                _autocomplete_cache[cache_key] = suggestions

            logger.info(
                f"Autocomplete: '{q_clean}' → "
                f"{len(suggestions)} suggestions"
            )

            return {
                "suggestions": suggestions,
                "from_cache":  False,
            }

    except httpx.TimeoutException:
        logger.warning(f"Autocomplete timeout: '{q_clean}'")
        return {"suggestions": [], "from_cache": False}

    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return {"suggestions": [], "from_cache": False}


@router.get("/drug-validate")
async def validate_drug(
    name: str = Query(
        ...,
        min_length=2,
        max_length=100,
    )
):
    """
    Quick validation check — is this a real drug name?
    Used by frontend to validate tags as user adds them.
    """
    result = await normalize_drug_name(name.strip())
    return {
        "input":          name,
        "valid":          result["found"],
        "canonical_name": result["normalized_name"] if result["found"] else None,
        "rxcui":          result.get("rxcui"),
    }


async def _get_drug_class(rxcui: Optional[str]) -> Optional[str]:
    """Fetch drug class from RxNorm for a given RxCUI."""
    if not rxcui:
        return None

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(
                f"{settings.rxnorm_base_url}"
                f"/rxcui/{rxcui}/classes.json"
            )

            if resp.status_code == 200:
                data    = resp.json()
                classes = (
                    data.get("rxclassDrugInfoList", {})
                        .get("rxclassDrugInfo", [])
                )

                if classes:
                    return classes[0].get(
                        "rxclassMinConceptItem", {}
                    ).get("className")

    except Exception:
        pass

    return None