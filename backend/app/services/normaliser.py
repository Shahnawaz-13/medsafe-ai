# app/services/normaliser.py
import httpx
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


async def normalize_drug(drug_name: str) -> dict:
    """
    Normalize a single drug name via RxNorm.

    Returns:
    {
        "input_name":       original input,
        "normalized_name":  best match name from RxNorm,
        "rxcui":            RxCUI string or None,
        "found":            True/False
    }
    """
    name = drug_name.strip()
    if not name:
        return _not_found(drug_name)

    # Strategy 1 — exact match
    result = await _exact_match(name)
    if result:
        return result

    # Strategy 2 — approximate match
    result = await _approximate_match(name)
    if result:
        return result

    logger.warning(f"RxNorm: no match for '{name}'")
    return _not_found(drug_name)


async def _exact_match(name: str) -> Optional[dict]:
    """
    GET /REST/rxcui.json?name={name}&search=1

    Response shape:
    {
      "idGroup": {
        "name": "Warfarin",
        "rxnormId": ["11289"]     <-- this is what we need
      }
    }
    """
    url = f"{RXNORM_BASE}/rxcui.json"
    params = {"name": name, "search": "1"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

            # Navigate the correct key path
            id_group = data.get("idGroup", {})
            rxnorm_ids = id_group.get("rxnormId")  # this is a LIST

            if rxnorm_ids and len(rxnorm_ids) > 0:
                rxcui = rxnorm_ids[0]
                normalized_name = id_group.get("name", name)
                logger.info(f"RxNorm exact: '{name}' → RxCUI {rxcui}")
                return {
                    "input_name":      name,
                    "normalized_name": normalized_name,
                    "rxcui":           rxcui,
                    "found":           True,
                }
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            logger.error(f"RxNorm exact HTTP error for '{name}': {e}")
    except Exception as e:
        logger.error(f"RxNorm exact error for '{name}': {e}")

    return None


async def _approximate_match(name: str) -> Optional[dict]:
    """
    GET /REST/approximateTerm.json?term={name}&maxEntries=5

    Response shape:
    {
      "approximateGroup": {
        "inputTerm": "Warfarin",
        "candidate": [
          {"rxcui": "11289", "rxaui": "...", "score": "100", "rank": "1"},
          ...
        ]
      }
    }
    """
    url = f"{RXNORM_BASE}/approximateTerm.json"
    params = {"term": name, "maxEntries": "5"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

            # Navigate the correct key path
            group = data.get("approximateGroup", {})
            candidates = group.get("candidate", [])  # this is a LIST of dicts

            if candidates:
                best = candidates[0]
                rxcui = best.get("rxcui")
                if rxcui:
                    # Fetch the proper name for this rxcui
                    normalized_name = await _get_name_for_rxcui(rxcui) or name
                    logger.info(f"RxNorm approx: '{name}' → RxCUI {rxcui}")
                    return {
                        "input_name":      name,
                        "normalized_name": normalized_name,
                        "rxcui":           rxcui,
                        "found":           True,
                    }
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            logger.error(f"RxNorm approx HTTP error for '{name}': {e}")
    except Exception as e:
        logger.error(f"RxNorm approx error for '{name}': {e}")

    return None


async def _get_name_for_rxcui(rxcui: str) -> Optional[str]:
    """
    GET /REST/rxcui/{rxcui}/properties.json
    Returns the official drug name for a given RxCUI.
    """
    url = f"{RXNORM_BASE}/rxcui/{rxcui}/properties.json"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            props = data.get("properties", {})
            return props.get("name")
    except Exception:
        return None


def _not_found(drug_name: str) -> dict:
    return {
        "input_name":      drug_name,
        "normalized_name": drug_name,
        "rxcui":           None,
        "found":           False,
    }


async def normalize_drug_list(drug_names: list[str]) -> list[dict]:
    """Normalize a list of drug names concurrently."""
    tasks = [normalize_drug(name) for name in drug_names]
    return await asyncio.gather(*tasks)


# ── Quick diagnostic — run: python -m app.services.normaliser ────────────────
if __name__ == "__main__":
    async def _debug():
        test_drugs = [
            "Warfarin", "Aspirin", "Metformin",
            "Lisinopril", "Atorvastatin", "xyzfake999"
        ]
        print(f"\nTesting {len(test_drugs)} drugs against RxNorm live API\n")
        results = await normalize_drug_list(test_drugs)
        for r in results:
            icon = "✅" if r["found"] else "❌"
            print(
                f"  {icon} {r['input_name']:15} → "
                f"{r['normalized_name']:30} | RxCUI: {r['rxcui']}"
            )
        found = sum(1 for r in results if r["found"])
        print(f"\nResult: {found}/{len(test_drugs)} resolved")

    asyncio.run(_debug())