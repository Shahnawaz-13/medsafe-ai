# app/services/alternative_service.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ── Curated safer alternatives map ────────────────────────────────────
# Format: "drug1_lower|drug2_lower": ["alternative_for_drug2"]
ALTERNATIVES_MAP = {
    "warfarin|aspirin":        ["Paracetamol", "Celecoxib"],
    "warfarin|ibuprofen":      ["Paracetamol", "Celecoxib"],
    "warfarin|naproxen":       ["Paracetamol"],
    "metformin|alcohol":       ["Avoid alcohol entirely"],
    "simvastatin|clarithromycin": ["Azithromycin", "Doxycycline"],
    "ssri|tramadol":           ["Codeine (with caution)", "Morphine"],
    "lisinopril|potassium":    ["Monitor potassium levels"],
    "digoxin|amiodarone":      ["Reduce digoxin dose", "Monitor ECG"],
    "sildenafil|nitroglycerin":["Consult cardiologist immediately"],
    "methotrexate|ibuprofen":  ["Paracetamol", "Avoid NSAIDs"],
}


def get_alternatives(
    drug1: str,
    drug2: str,
    severity: str,
) -> List[str]:
    """
    Return safer alternative suggestions for a drug pair.
    Only returns alternatives for moderate/high/contraindicated.
    """
    # Low severity and none don't need alternatives
    if severity in ["low", "none"]:
        return []

    # Build lookup key (order-independent)
    d1_lower = (drug1 or "").strip().lower()
    d2_lower = (drug2 or "").strip().lower()

    key1 = f"{d1_lower}|{d2_lower}"
    key2 = f"{d2_lower}|{d1_lower}"

    # Check both orders
    alternatives = (
        ALTERNATIVES_MAP.get(key1) or
        ALTERNATIVES_MAP.get(key2) or
        []
    )

    if alternatives:
        logger.info(
            f"Alternatives found for "
            f"'{drug1}' + '{drug2}': {alternatives}"
        )
    else:
        logger.info(
            f"No alternatives mapped for "
            f"'{drug1}' + '{drug2}'"
        )

    return alternatives


def get_alternatives_for_pairs(
    resolved_pairs: List[Dict],
) -> List[Dict]:
    """
    Add safer alternatives to all resolved interaction pairs.
    Returns enriched pairs list.
    """
    enriched = []
    for pair in resolved_pairs:
        drug1    = pair.get("drug1", "")
        drug2    = pair.get("drug2", "")
        severity = pair.get("severity", "none")

        alternatives = get_alternatives(drug1, drug2, severity)

        enriched.append({
            **pair,
            "safer_alternatives": alternatives,
        })

    return enriched