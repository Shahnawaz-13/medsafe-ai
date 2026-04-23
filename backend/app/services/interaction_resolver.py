# app/services/interaction_resolver.py
import httpx
import asyncio
import logging
from typing import List, Dict, Tuple, Optional
from app.config import settings
from app.services.cache_service import (
    get_cached_interaction,
    store_interaction_cache,
)
from app.services.severity_classifier import classify_severity

logger = logging.getLogger(__name__)

OPENFDA_BASE = "https://api.fda.gov/drug"
TIMEOUT      = 8.0   # increased from 6.0

# ── Known brand → generic mappings ───────────────────────────────────
BRAND_TO_GENERIC = {
    "advil":      "ibuprofen",
    "tylenol":    "acetaminophen",
    "motrin":     "ibuprofen",
    "coumadin":   "warfarin",
    "glucophage": "metformin",
    "zocor":      "simvastatin",
    "lipitor":    "atorvastatin",
    "plavix":     "clopidogrel",
    "zithromax":  "azithromycin",
    "amoxil":     "amoxicillin",
    "augmentin":  "amoxicillin",
    "prozac":     "fluoxetine",
    "zoloft":     "sertraline",
    "prinivil":   "lisinopril",
    "norvasc":    "amlodipine",
    "synthroid":  "levothyroxine",
    "lasix":      "furosemide",
    "diflucan":   "fluconazole",
    "flagyl":     "metronidazole",
    "valium":     "diazepam",
}


def get_search_variants(drug_name: str) -> List[str]:
    """
    Generate multiple search variants for a drug name.
    Handles brand names, generics, and capitalisation.
    """
    name_lower = drug_name.lower().strip()
    variants   = [drug_name, drug_name.lower(), drug_name.upper()]

    # Add generic if brand name provided
    if name_lower in BRAND_TO_GENERIC:
        generic = BRAND_TO_GENERIC[name_lower]
        variants.extend([generic, generic.capitalize()])

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)

    return unique


async def resolve_interaction(
    drug_a: Dict,
    drug_b: Dict,
) -> Dict:
    """
    Resolve interaction between two drugs.
    Strategy: Cache → OpenFDA Label → Adverse Events → Empty
    """
    drug1_name = drug_a.get("normalized_name", drug_a["input_name"])
    drug2_name = drug_b.get("normalized_name", drug_b["input_name"])
    rxcui1     = drug_a.get("rxcui")
    rxcui2     = drug_b.get("rxcui")

    # ── Step 1: Cache check ───────────────────────────────────────
    cached = await get_cached_interaction(
        rxcui1, rxcui2, drug1_name, drug2_name
    )
    if cached:
        logger.info(f"Cache HIT: {drug1_name} + {drug2_name}")
        return _build_result(
            drug1_name, drug2_name,
            cached.get("interaction_data", {}),
            cached.get("found", False),
            from_cache=True,
        )

    # ── Step 2: Query OpenFDA ─────────────────────────────────────
    raw_data = await _query_openfda_all_strategies(
        drug1_name, drug2_name
    )

    # ── Step 3: Store in cache ────────────────────────────────────
    await store_interaction_cache(
        rxcui1=rxcui1,
        rxcui2=rxcui2,
        drug1_name=drug1_name,
        drug2_name=drug2_name,
        interaction_data=raw_data,
        found=raw_data.get("found", False),
        source=raw_data.get("source", "OpenFDA"),
    )

    return _build_result(
        drug1_name, drug2_name,
        raw_data,
        raw_data.get("found", False),
        from_cache=False,
    )


async def _query_openfda_all_strategies(
    drug1_name: str,
    drug2_name: str,
) -> Dict:
    """
    Try all search strategies to find interaction data.
    Returns the first successful result.
    """
    base_params = {}
    if settings.openfda_api_key:
        base_params["api_key"] = settings.openfda_api_key

    # Get all name variants for both drugs
    drug1_variants = get_search_variants(drug1_name)
    drug2_variants = get_search_variants(drug2_name)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        # Strategy 1: Label search with all variants
        for d1 in drug1_variants:
            for d2 in drug2_variants:
                result = await _search_label(
                    client, d1, d2, base_params
                )
                if result.get("found"):
                    logger.info(
                        f"OpenFDA Strategy 1: "
                        f"'{d1}' label mentions '{d2}'"
                    )
                    result["drug1"] = drug1_name
                    result["drug2"] = drug2_name
                    return result

        # Strategy 2: Reverse label search
        for d2 in drug2_variants:
            for d1 in drug1_variants:
                result = await _search_label(
                    client, d2, d1, base_params
                )
                if result.get("found"):
                    logger.info(
                        f"OpenFDA Strategy 2 (reverse): "
                        f"'{d2}' label mentions '{d1}'"
                    )
                    result["drug1"] = drug1_name
                    result["drug2"] = drug2_name
                    return result

        # Strategy 3: Full-text interaction search
        result = await _search_fulltext(
            client, drug1_name, drug2_name, base_params
        )
        if result.get("found"):
            logger.info(
                f"OpenFDA Strategy 3 (fulltext): "
                f"'{drug1_name}' + '{drug2_name}'"
            )
            return result

        # Strategy 4: Adverse event reports
        result = await _search_events(
            client, drug1_name, drug2_name, base_params
        )
        if result.get("found"):
            logger.info(
                f"OpenFDA Strategy 4 (events): "
                f"'{drug1_name}' + '{drug2_name}'"
            )
            return result

    logger.info(
        f"No interaction found: '{drug1_name}' + '{drug2_name}'"
    )
    return {
        "drug1":            drug1_name,
        "drug2":            drug2_name,
        "interaction_text": "",
        "found":            False,
        "source":           "OpenFDA",
    }


async def _search_label(
    client: httpx.AsyncClient,
    primary: str,
    secondary: str,
    base_params: Dict,
) -> Dict:
    """Search OpenFDA drug label for interaction mention."""
    try:
        # Try brand name search first
        params = {
            **base_params,
            "search": (
                f'(openfda.brand_name:"{primary}" '
                f'OR openfda.generic_name:"{primary}") '
                f'AND drug_interactions:"{secondary}"'
            ),
            "limit": 1,
        }

        resp = await client.get(
            f"{OPENFDA_BASE}/label.json",
            params=params,
        )

        if resp.status_code == 200:
            data    = resp.json()
            results = data.get("results", [])
            if results:
                return _extract_from_label(
                    results[0], primary, secondary
                )

        # Simpler fallback search
        params2 = {
            **base_params,
            "search": f'drug_interactions:"{secondary}"',
            "limit":  5,
        }
        resp2 = await client.get(
            f"{OPENFDA_BASE}/label.json",
            params=params2,
        )

        if resp2.status_code == 200:
            data    = resp2.json()
            results = data.get("results", [])
            for label in results:
                if _label_matches_drug(label, primary):
                    return _extract_from_label(
                        label, primary, secondary
                    )

    except httpx.TimeoutException:
        logger.warning(f"Label search timeout: {primary}+{secondary}")
    except Exception as e:
        logger.error(f"Label search error: {e}")

    return {"found": False}


async def _search_fulltext(
    client: httpx.AsyncClient,
    drug1: str,
    drug2: str,
    base_params: Dict,
) -> Dict:
    """Full-text search in drug interaction sections."""
    try:
        params = {
            **base_params,
            "search": (
                f'drug_interactions:"{drug1}" '
                f'AND drug_interactions:"{drug2}"'
            ),
            "limit": 3,
        }
        resp = await client.get(
            f"{OPENFDA_BASE}/label.json",
            params=params,
        )

        if resp.status_code == 200:
            data    = resp.json()
            results = data.get("results", [])
            if results:
                label        = results[0]
                interactions = label.get("drug_interactions", [])
                if interactions:
                    full_text = " ".join(interactions)
                    relevant  = _extract_window(
                        full_text, drug2, window=600
                    )
                    return {
                        "drug1":            drug1,
                        "drug2":            drug2,
                        "interaction_text": relevant,
                        "found":            True,
                        "source":           "OpenFDA Fulltext",
                    }

    except Exception as e:
        logger.error(f"Fulltext search error: {e}")

    return {"found": False}


async def _search_events(
    client: httpx.AsyncClient,
    drug1: str,
    drug2: str,
    base_params: Dict,
) -> Dict:
    """Search FDA adverse event reports for drug pair."""
    try:
        params = {
            **base_params,
            "search": (
                f'patient.drug.medicinalproduct:"{drug1}" '
                f'AND patient.drug.medicinalproduct:"{drug2}"'
            ),
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": 8,
        }
        resp = await client.get(
            f"{OPENFDA_BASE}/event.json",
            params=params,
        )

        if resp.status_code == 200:
            data    = resp.json()
            results = data.get("results", [])
            if results:
                reactions = [
                    r.get("term", "").lower()
                    for r in results[:5]
                ]
                text = (
                    f"FDA adverse event reports show that when "
                    f"{drug1} and {drug2} are taken together, "
                    f"the following reactions have been reported: "
                    f"{', '.join(reactions)}. "
                    f"Total reports in FDA database indicate "
                    f"this combination warrants caution. "
                    f"Please consult your doctor or pharmacist."
                )
                return {
                    "drug1":            drug1,
                    "drug2":            drug2,
                    "interaction_text": text,
                    "found":            True,
                    "source":           "OpenFDA Events",
                }

    except Exception as e:
        logger.error(f"Events search error: {e}")

    return {"found": False}


def _extract_from_label(
    label: Dict,
    primary: str,
    secondary: str,
) -> Dict:
    """Extract interaction text from a drug label."""
    interactions = label.get("drug_interactions", [])
    if not interactions:
        return {"found": False}

    full_text = " ".join(interactions)
    relevant  = _extract_window(full_text, secondary, window=600)

    return {
        "drug1":            primary,
        "drug2":            secondary,
        "interaction_text": relevant or full_text[:500],
        "found":            True,
        "source":           "OpenFDA Label",
    }


def _label_matches_drug(label: Dict, drug_name: str) -> bool:
    """Check if a label belongs to the given drug."""
    openfda     = label.get("openfda", {})
    brand_names = [
        n.lower() for n in openfda.get("brand_name", [])
    ]
    generic_names = [
        n.lower() for n in openfda.get("generic_name", [])
    ]
    all_names   = brand_names + generic_names
    name_lower  = drug_name.lower()

    return any(name_lower in n or n in name_lower for n in all_names)


def _extract_window(
    text: str,
    keyword: str,
    window: int = 600,
) -> str:
    """Extract text window around keyword mention."""
    text_lower    = text.lower()
    keyword_lower = keyword.lower()
    idx           = text_lower.find(keyword_lower)

    if idx == -1:
        return text[:window]

    start = max(0, idx - 150)
    end   = min(len(text), idx + window)
    return text[start:end].strip()


def _build_result(
    drug1_name: str,
    drug2_name: str,
    interaction_data: Dict,
    found: bool,
    from_cache: bool = False,
) -> Dict:
    """Build standardised interaction result."""
    interaction_text = interaction_data.get("interaction_text", "")
    severity = (
        classify_severity(interaction_text) if found else "none"
    )

    return {
        "drug1":            drug1_name,
        "drug2":            drug2_name,
        "interaction_text": interaction_text,
        "found":            found,
        "severity":         severity,
        "source":           interaction_data.get("source", "OpenFDA"),
        "from_cache":       from_cache,
    }


async def resolve_all_pairs(
    pairs: List[Tuple[Dict, Dict]],
) -> List[Dict]:
    """Resolve all drug pairs concurrently."""
    if not pairs:
        return []

    tasks = [
        resolve_interaction(drug_a, drug_b)
        for drug_a, drug_b in pairs
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    cleaned = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            drug_a, drug_b = pairs[i]
            logger.error(
                f"Pair failed: "
                f"'{drug_a.get('normalized_name')}' + "
                f"'{drug_b.get('normalized_name')}': {result}"
            )
            cleaned.append({
                "drug1":      drug_a.get("normalized_name", "Unknown"),
                "drug2":      drug_b.get("normalized_name", "Unknown"),
                "interaction_text": "",
                "found":      False,
                "severity":   "none",
                "source":     "error",
                "from_cache": False,
            })
        else:
            cleaned.append(result)

    return cleaned