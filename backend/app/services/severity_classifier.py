# app/services/severity_classifier.py
import logging
from typing import List
from app.models.interaction import Severity

logger = logging.getLogger(__name__)

# ── Keyword lists (order matters — check highest first) ───────────────
CONTRAINDICATED_KEYWORDS = [
    "contraindicated", "do not use", "must not",
    "never combine", "life-threatening", "fatal",
    "death", "avoid combination", "should not be used",
    "absolutely contraindicated",
]

HIGH_KEYWORDS = [
    "serious", "severe", "significant risk", "major",
    "hospitalization", "hospitalisation", "bleeding risk",
    "cardiac arrest", "seizure", "toxicity", "dangerous",
    "avoid unless", "potentially fatal", "haemorrhage",
    "hemorrhage", "coma", "respiratory depression",
]

MODERATE_KEYWORDS = [
    "moderate", "monitor closely", "use caution",
    "may increase", "may decrease", "reduced efficacy",
    "altered levels", "adjust dose", "dosage adjustment",
    "close monitoring", "increased risk", "caution advised",
]

LOW_KEYWORDS = [
    "minor", "minimal", "slight", "low risk",
    "unlikely to", "generally safe", "small effect",
    "clinically insignificant", "marginal",
]


def classify_severity(interaction_text: str) -> str:
    """
    Classify severity of a drug interaction from raw text.

    Priority order:
    CONTRAINDICATED → HIGH → MODERATE → LOW → NONE
    """
    if not interaction_text:
        return Severity.none

    text_lower = interaction_text.lower()

    # Check in priority order (highest first)
    for keyword in CONTRAINDICATED_KEYWORDS:
        if keyword in text_lower:
            logger.debug(
                f"Severity CONTRAINDICATED — "
                f"matched keyword: '{keyword}'"
            )
            return Severity.contraindicated

    for keyword in HIGH_KEYWORDS:
        if keyword in text_lower:
            logger.debug(
                f"Severity HIGH — matched keyword: '{keyword}'"
            )
            return Severity.high

    for keyword in MODERATE_KEYWORDS:
        if keyword in text_lower:
            logger.debug(
                f"Severity MODERATE — matched keyword: '{keyword}'"
            )
            return Severity.moderate

    for keyword in LOW_KEYWORDS:
        if keyword in text_lower:
            logger.debug(
                f"Severity LOW — matched keyword: '{keyword}'"
            )
            return Severity.low

    return Severity.none


def get_severity_emoji(severity: str) -> str:
    """Return emoji for a given severity level."""
    emojis = {
        Severity.contraindicated: "🚫",
        Severity.high:            "🔴",
        Severity.moderate:        "🟡",
        Severity.low:             "🟢",
        Severity.none:            "⚪",
    }
    return emojis.get(severity, "⚪")


def get_overall_severity(severities: List[str]) -> str:
    """
    Return the highest severity from a list.
    Priority: contraindicated > high > moderate > low > none
    """
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