# app/services/normaliser.py
import httpx
import asyncio
import logging
from typing import List, Dict, Optional
from app.config import settings
from app.utils.helpers import sanitize_drug_name

logger = logging.getLogger(__name__)

RXNORM_BASE = settings.rxnorm_base_url
TIMEOUT     = 4.0   # seconds


async def normalize_drug_name(drug_name: str) -> Dict:
    """
    Normalize a single drug name to its canonical RxNorm form.

    Returns dict with:
      - input_name:       original input
      - normalized_name:  canonical name from RxNorm
      - rxcui:            RxNorm concept unique identifier
      - found:            True if matched in RxNorm
    """
    clean_name = sanitize_drug_name(drug_name)

    if not clean_name or len(clean_name) < 2:
        return _not_found(drug_name)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Try exact match first (faster)
            exact = await _try_exact_match(client, clean_name)
            if exact:
                logger.info(
                    f"RxNorm exact match: '{drug_name}' → "
                    f"'{exact['normalized_name']}' ({exact['rxcui']})"
                )
                return exact

            # Fall back to approximate match
            approx = await _try_approx_match(client, clean_name)
            if approx:
                logger.info(
                    f"RxNorm approx match: '{drug_name}' → "
                    f"'{approx['normalized_name']}' ({approx['rxcui']})"
                )
                return approx

            logger.warning(f"RxNorm: no match for '{drug_name}'")
            return _not_found(drug_name)

    except httpx.TimeoutException:
        logger.error(f"RxNorm timeout for '{drug_name}'")
        return _not_found(drug_name)
    except Exception as e:
        logger.error(f"RxNorm error for '{drug_name}': {e}")
        return _not_found(drug_name)


async def _try_exact_match(
    client: httpx.AsyncClient,
    name: str
) -> Optional[Dict]:
    """Try RxNorm exact drug name lookup."""
    try:
        url = f"{RXNORM_BASE}/drugs.json"
        resp = await client.get(url, params={"name": name})

        if resp.status_code != 200:
            return None

        data = resp.json()
        drug_group = data.get("drugGroup", {})
        concept_group = drug_group.get("conceptGroup", [])

        for group in concept_group:
            concepts = group.get("conceptProperties", [])
            if concepts:
                best = concepts[0]
                return {
                    "input_name":      name,
                    "normalized_name": best.get("name", name),
                    "rxcui":           best.get("rxcui"),
                    "found":           True,
                }
    except Exception:
        pass
    return None


async def _try_approx_match(
    client: httpx.AsyncClient,
    name: str
) -> Optional[Dict]:
    """Try RxNorm approximate term matching."""
    try:
        url = f"{RXNORM_BASE}/approximateTerm.json"
        resp = await client.get(
            url,
            params={"term": name, "maxEntries": 1}
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        approx_group = data.get("approximateGroup", {})
        candidates = approx_group.get("candidate", [])

        if candidates:
            best = candidates[0]
            rxcui = best.get("rxcui")
            # Get full name from rxcui
            name_result = await _get_name_from_rxcui(
                client, rxcui
            )
            return {
                "input_name":      name,
                "normalized_name": name_result or name,
                "rxcui":           rxcui,
                "found":           True,
            }
    except Exception:
        pass
    return None


async def _get_name_from_rxcui(
    client: httpx.AsyncClient,
    rxcui: str
) -> Optional[str]:
    """Get canonical drug name from RxCUI."""
    try:
        url = f"{RXNORM_BASE}/rxcui/{rxcui}/properties.json"
        resp = await client.get(url)

        if resp.status_code == 200:
            data = resp.json()
            props = data.get("properties", {})
            return props.get("name")
    except Exception:
        pass
    return None


def _not_found(drug_name: str) -> Dict:
    """Return a standardised not-found result."""
    return {
        "input_name":      drug_name,
        "normalized_name": drug_name,
        "rxcui":           None,
        "found":           False,
    }


async def normalize_drug_list(drug_names: List[str]) -> List[Dict]:
    """
    Normalize a list of drug names concurrently.
    Uses asyncio.gather for parallel API calls.
    """
    tasks = [normalize_drug_name(name) for name in drug_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Replace any exceptions with not-found results
    cleaned = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(
                f"Normalisation failed for "
                f"'{drug_names[i]}': {result}"
            )
            cleaned.append(_not_found(drug_names[i]))
        else:
            cleaned.append(result)

    return cleaned