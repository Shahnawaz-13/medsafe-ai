# tests/test_day8.py
import pytest
from app.services.interaction_resolver import (
    get_search_variants,
    _extract_window,
    _label_matches_drug,
    _build_result,
)
from app.services.alternative_service import (
    get_alternatives,
    get_alternatives_for_pairs,
)


# ── Search variant tests ──────────────────────────────────────────────
def test_brand_name_returns_generic():
    variants = get_search_variants("Advil")
    assert "ibuprofen" in [v.lower() for v in variants]


def test_generic_name_has_variants():
    variants = get_search_variants("warfarin")
    assert len(variants) >= 2
    assert "warfarin" in [v.lower() for v in variants]


def test_variants_no_duplicates():
    variants = get_search_variants("Aspirin")
    assert len(variants) == len(set(variants))


def test_coumadin_maps_to_warfarin():
    variants = get_search_variants("Coumadin")
    assert "warfarin" in [v.lower() for v in variants]


# ── Extract window tests ──────────────────────────────────────────────
def test_extract_window_finds_keyword():
    text   = "A" * 200 + " aspirin causes bleeding " + "B" * 200
    result = _extract_window(text, "aspirin", window=300)
    assert "aspirin" in result.lower()


def test_extract_window_keyword_not_found():
    text   = "General drug information text here."
    result = _extract_window(text, "warfarin")
    assert len(result) <= 600


def test_extract_window_respects_limit():
    text   = "X" * 2000
    result = _extract_window(text, "notfound", window=400)
    assert len(result) <= 400


# ── Build result tests ────────────────────────────────────────────────
def test_build_result_severity_assigned():
    data = {
        "interaction_text": "Serious risk of bleeding.",
        "source": "OpenFDA"
    }
    result = _build_result("Warfarin", "Aspirin", data, found=True)
    assert result["severity"] in ["high", "moderate"]
    assert result["drug1"] == "Warfarin"
    assert result["drug2"] == "Aspirin"
    assert result["found"] is True


def test_build_result_not_found_is_none():
    result = _build_result("Drug A", "Drug B", {}, found=False)
    assert result["severity"] == "none"
    assert result["found"] is False


# ── Alternatives tests ────────────────────────────────────────────────
def test_warfarin_aspirin_has_alternatives():
    alts = get_alternatives("Warfarin", "Aspirin", "high")
    assert len(alts) > 0
    assert "Paracetamol" in alts


def test_order_independent_alternatives():
    alts1 = get_alternatives("Warfarin", "Aspirin", "high")
    alts2 = get_alternatives("Aspirin", "Warfarin", "high")
    assert alts1 == alts2


def test_low_severity_no_alternatives():
    alts = get_alternatives("Drug A", "Drug B", "low")
    assert alts == []


def test_none_severity_no_alternatives():
    alts = get_alternatives("Drug A", "Drug B", "none")
    assert alts == []


def test_enrich_pairs_adds_alternatives():
    pairs = [
        {
            "drug1":    "Warfarin",
            "drug2":    "Aspirin",
            "severity": "high",
            "found":    True,
        }
    ]
    enriched = get_alternatives_for_pairs(pairs)
    assert len(enriched) == 1
    assert "safer_alternatives" in enriched[0]
    assert len(enriched[0]["safer_alternatives"]) > 0