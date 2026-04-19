# tests/test_normaliser.py
import pytest
from app.services.normaliser import (
    normalize_drug_name,
    normalize_drug_list,
    _not_found,
    sanitize_drug_name,
)
from app.utils.helpers import sanitize_drug_name


@pytest.mark.asyncio
async def test_normalize_known_drug():
    result = await normalize_drug_name("Warfarin")
    assert result["found"] is True
    assert result["rxcui"] is not None
    assert "warfarin" in result["normalized_name"].lower()


@pytest.mark.asyncio
async def test_normalize_lowercase():
    result = await normalize_drug_name("aspirin")
    assert result["found"] is True
    assert result["rxcui"] is not None


@pytest.mark.asyncio
async def test_normalize_unknown_drug():
    result = await normalize_drug_name("xyzabc99999fake")
    assert result["found"] is False
    assert result["rxcui"] is None
    assert result["input_name"] == "xyzabc99999fake"


@pytest.mark.asyncio
async def test_normalize_empty_string():
    result = await normalize_drug_name("")
    assert result["found"] is False


@pytest.mark.asyncio
async def test_normalize_list_concurrent():
    drugs = ["Warfarin", "Aspirin", "Metformin"]
    results = await normalize_drug_list(drugs)
    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results)
    found_count = sum(1 for r in results if r["found"])
    assert found_count >= 2   # at least 2 of 3 should be found