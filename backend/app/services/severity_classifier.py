# app/services/severity_classifier.py
import re
import logging
# from typing import List, Optional
from typing import Dict, List, Optional, Tuple
from app.models.interaction import Severity

logger = logging.getLogger(__name__)

# ── Keyword patterns (order = priority) ──────────────────────────────
CONTRAINDICATED_PATTERNS = [
    r"\bcontraindicated\b",
    r"\bdo not (use|take|administer)\b",
    r"\bmust not (be used|take)\b",
    r"\bnever (combine|use together)\b",
    r"\blife.threatening\b",
    r"\bfatal(ly)?\b",
    r"\bavoid (combination|concomitant use)\b",
    r"\babsolutely contraindicated\b",
]

HIGH_PATTERNS = [
    r"\bserious(ly)?\b",
    r"\bsevere(ly)?\b",
    r"\bsignificant risk\b",
    r"\bmajor (interaction|risk)\b",
    r"\bhospitali[sz]ation\b",
    r"\bbleeding risk\b",
    r"\bcardiac arrest\b",
    r"\bseizure\b",
    r"\btoxicity\b",
    r"\bdangerous(ly)?\b",
    r"\bhaemorr?hage\b",
    r"\bcoma\b",
    r"\brespiratory depression\b",
    r"\bpotentially fatal\b",
    r"\bserotonin syndrome\b",
    r"\brhabdomyolysis\b",
    r"\bQT prolongation\b",
]

MODERATE_PATTERNS = [
    r"\bmoderate\b",
    r"\bmonitor closely\b",
    r"\buse caution\b",
    r"\bmay (increase|decrease|affect)\b",
    r"\breduced efficacy\b",
    r"\baltered (levels|effect)\b",
    r"\bdosage? adjustment\b",
    r"\bclose monitoring\b",
    r"\bcaution (is )?advised\b",
    r"\bincreased risk\b",
    r"\bclinically significant\b",
]

LOW_PATTERNS = [
    r"\bminor\b",
    r"\bminimal(ly)?\b",
    r"\bslight(ly)?\b",
    r"\blow risk\b",
    r"\bunlikely to\b",
    r"\bgenerally safe\b",
    r"\bsmall effect\b",
    r"\bclinically insignificant\b",
    r"\bmarginal\b",
]


def classify_severity(interaction_text: Optional[str]) -> str:
    """
    Classify severity from interaction text using regex patterns.
    Priority: CONTRAINDICATED > HIGH > MODERATE > LOW > NONE
    """
    if not interaction_text:
        return Severity.none

    text_lower = interaction_text.lower()

    # Check each level in priority order
    for pattern in CONTRAINDICATED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.debug(
                f"Severity CONTRAINDICATED — pattern: '{pattern}'"
            )
            return Severity.contraindicated

    for pattern in HIGH_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.debug(
                f"Severity HIGH — pattern: '{pattern}'"
            )
            return Severity.high

    for pattern in MODERATE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.debug(
                f"Severity MODERATE — pattern: '{pattern}'"
            )
            return Severity.moderate

    for pattern in LOW_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.debug(
                f"Severity LOW — pattern: '{pattern}'"
            )
            return Severity.low

    return Severity.none


def get_severity_emoji(severity: str) -> str:
    """Return emoji for a severity level."""
    return {
        Severity.contraindicated: "🚫",
        Severity.high:            "🔴",
        Severity.moderate:        "🟡",
        Severity.low:             "🟢",
        Severity.none:            "⚪",
    }.get(severity, "⚪")


def get_overall_severity(severities: List[str]) -> str:
    """Return highest severity from a list."""
    priority = [
        Severity.contraindicated,
        Severity.high,
        Severity.moderate,
        Severity.low,
        Severity.none,
    ]
    for level in priority:
        if level in severities:
            return level
    return Severity.none


def severity_to_display(severity: str) -> dict:
    """Return full display config for a severity level."""
    configs = {
        Severity.contraindicated: {
            "label":       "CONTRAINDICATED",
            "emoji":       "🚫",
            "color":       "red",
            "action":      "Do NOT take together. Contact your doctor immediately.",
            "urgent":      True,
        },
        Severity.high: {
            "label":       "HIGH SEVERITY",
            "emoji":       "🔴",
            "color":       "orange",
            "action":      "Consult your doctor before taking these together.",
            "urgent":      True,
        },
        Severity.moderate: {
            "label":       "MODERATE",
            "emoji":       "🟡",
            "color":       "yellow",
            "action":      "Monitor closely. Discuss with your doctor.",
            "urgent":      False,
        },
        Severity.low: {
            "label":       "LOW",
            "emoji":       "🟢",
            "color":       "green",
            "action":      "Mention at your next routine check-up.",
            "urgent":      False,
        },
        Severity.none: {
            "label":       "NO INTERACTION",
            "emoji":       "⚪",
            "color":       "gray",
            "action":      "No known interaction detected.",
            "urgent":      False,
        },
    }
    return configs.get(severity, configs[Severity.none])


# Fix missing import
from typing import Dict