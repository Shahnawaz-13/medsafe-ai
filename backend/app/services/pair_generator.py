# app/services/pair_generator.py
import logging
from itertools import combinations
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


def generate_pairs(
    drugs: List[Dict]
) -> List[Tuple[Dict, Dict]]:
    """
    Generate all unique drug pairs from a list.

    For n drugs: n*(n-1)/2 pairs
    Examples:
      3 drugs → 3 pairs
      4 drugs → 6 pairs
      5 drugs → 10 pairs

    Filters out pairs where both drugs have no rxcui.
    """
    if len(drugs) < 2:
        logger.warning("Need at least 2 drugs to generate pairs")
        return []

    all_pairs = list(combinations(drugs, 2))

    # Filter: at least one drug in pair must have an rxcui
    # (can't look up interaction without any identifier)
    valid_pairs = []
    for drug_a, drug_b in all_pairs:
        if drug_a.get("rxcui") or drug_b.get("rxcui"):
            valid_pairs.append((drug_a, drug_b))
        else:
            logger.warning(
                f"Skipping pair: both drugs unidentified — "
                f"'{drug_a['input_name']}' + '{drug_b['input_name']}'"
            )

    logger.info(
        f"Generated {len(valid_pairs)} valid pairs "
        f"from {len(drugs)} drugs "
        f"({len(all_pairs) - len(valid_pairs)} skipped)"
    )

    return valid_pairs


def get_pair_count(drug_count: int) -> int:
    """Calculate expected number of pairs for n drugs."""
    return drug_count * (drug_count - 1) // 2