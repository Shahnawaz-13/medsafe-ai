# tests/test_interaction_resolver.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.interaction_resolver import (
    resolve_interaction,
    resolve_all_pairs,
    _extract_relevant_text,
    _build_result,
)
from app.services.cache_service import (
    get_cached_interaction,
    store_interaction_cache,
)


# ── Unit tests (no real API calls) ───────────────────────────────────

def test_extract_relevant_text_finds_drug():
    """Should extract text window around drug mention."""
    text   = "A" * 200 + "aspirin causes bleeding" + "B" * 200
    result = _extract_relevant_text(text, "aspirin")
    assert "aspirin" in result.lower()


def test_extract_relevant_text_not_found():
    """Should return first 400 chars if drug not mentioned."""
    text   = "Some generic text without any drug name mentioned here."
    result = _extract_relevant_text(text, "warfarin")
    assert len(result) <= 400


def test_build_result_found():
    """Should build complete result dict."""
    result = _build_result(
        "Warfarin", "Aspirin",
        {"interaction_text": "serious bleeding risk", "source": "OpenFDA"},
        found=True,
    )
    assert result["drug1"]   == "Warfarin"
    assert result["drug2"]   == "Aspirin"
    assert result["found"]   is True
    assert result["severity"] in ["high", "moderate", "low",
                                  "contraindicated", "none"]


def test_build_result_not_found():
    """Should return none severity when not found."""
    result = _build_result(
        "Drug A", "Drug B", {}, found=False
    )
    assert result["found"]    is False
    assert result["severity"] == "none"


# ── Integration tests (real API — skip if offline) ───────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_resolve_known_interaction():
    """
    Warfarin + Aspirin is a well-known HIGH interaction.
    This test hits the real OpenFDA API.
    """
    from app.database import connect_db, close_db
    await connect_db()

    drug_a = {
        "input_name":      "Warfarin",
        "normalized_name": "Warfarin",
        "rxcui":           "11289",
    }
    drug_b = {
        "input_name":      "Aspirin",
        "normalized_name": "Aspirin",
        "rxcui":           "1191",
    }

    result = await resolve_interaction(drug_a, drug_b)

    assert result["drug1"] == "Warfarin"
    assert result["drug2"] == "Aspirin"
    assert isinstance(result["found"], bool)
    assert result["severity"] in [
        "none", "low", "moderate", "high", "contraindicated"
    ]

    await close_db()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_resolve_all_pairs_returns_correct_count():
    """Should return one result per pair."""
    from app.database import connect_db, close_db
    await connect_db()

    pairs = [
        (
            {"input_name": "Warfarin",   "normalized_name": "Warfarin",
             "rxcui": "11289"},
            {"input_name": "Aspirin",    "normalized_name": "Aspirin",
             "rxcui": "1191"},
        ),
        (
            {"input_name": "Metformin",  "normalized_name": "Metformin",
             "rxcui": "6809"},
            {"input_name": "Lisinopril", "normalized_name": "Lisinopril",
             "rxcui": "29046"},
        ),
    ]

    results = await resolve_all_pairs(pairs)
    assert len(results) == 2
    assert all("drug1" in r and "drug2" in r for r in results)

    await close_db()