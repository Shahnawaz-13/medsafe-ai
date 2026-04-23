# tests/test_analyze_route.py
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from main import app


# ── Mock AI response ──────────────────────────────────────────────────
MOCK_AI_RESPONSE = {
    "interactions": [
        {
            "drug1":             "Warfarin",
            "drug2":             "Aspirin",
            "severity":          "high",
            "severity_emoji":    "🔴",
            "plain_explanation": (
                "Warfarin and Aspirin both affect blood clotting. "
                "Taking them together significantly raises your "
                "risk of serious bleeding. Please consult your "
                "doctor immediately."
            ),
            "what_to_watch_for": "Unusual bruising.",
            "action_required":   "See your doctor.",
            "safer_alternatives": ["Paracetamol"],
            "mechanism":         "Pharmacodynamic synergy",
            "sources":           ["OpenFDA"],
        }
    ],
    "overall_severity": "high",
    "summary":          "1 high-severity interaction found.",
    "disclaimer":       "Educational purposes only.",
}

MOCK_NORMALIZED = [
    {
        "input_name":      "Warfarin",
        "normalized_name": "Warfarin",
        "rxcui":           "11289",
        "found":           True,
    },
    {
        "input_name":      "Aspirin",
        "normalized_name": "Aspirin",
        "rxcui":           "1191",
        "found":           True,
    },
]

MOCK_RESOLVED = [
    {
        "drug1":            "Warfarin",
        "drug2":            "Aspirin",
        "interaction_text": "Serious bleeding risk.",
        "found":            True,
        "severity":         "high",
        "source":           "OpenFDA",
        "from_cache":       False,
        "safer_alternatives": ["Paracetamol"],
    }
]


@pytest.fixture
def mock_pipeline():
    """Mock the full pipeline for route testing."""
    with patch(
        "app.routers.analyze.normalize_drug_list",
        new_callable=AsyncMock,
        return_value=MOCK_NORMALIZED,
    ) as mock_norm, patch(
        "app.routers.analyze.resolve_all_pairs",
        new_callable=AsyncMock,
        return_value=MOCK_RESOLVED,
    ) as mock_resolve, patch(
        "app.routers.analyze.get_interaction_explanations",
        new_callable=AsyncMock,
        return_value=MOCK_AI_RESPONSE,
    ) as mock_ai, patch(
        "app.routers.analyze.get_db",
        return_value=None,   # Skip MongoDB for unit tests
    ):
        yield {
            "normalize":  mock_norm,
            "resolve":    mock_resolve,
            "ai":         mock_ai,
        }


@pytest.mark.asyncio
async def test_analyze_success(mock_pipeline):
    """Full successful analysis returns 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": ["Warfarin", "Aspirin"]},
        )

    assert response.status_code == 200
    data = response.json()

    assert "check_id"         in data
    assert "pairs"            in data
    assert "overall_severity" in data
    assert "disclaimer"       in data
    assert "response_time_ms" in data
    assert data["overall_severity"] == "high"


@pytest.mark.asyncio
async def test_analyze_with_patient_context(mock_pipeline):
    """Analysis with patient context returns 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={
                "drugs":     ["Warfarin", "Aspirin"],
                "age":       65,
                "gender":    "Male",
                "allergies": ["Penicillin"],
            },
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyze_single_drug():
    """Single drug returns 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": ["Warfarin"]},
        )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_analyze_empty_drugs():
    """Empty drug list returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": []},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_too_many_drugs():
    """16+ drugs returns 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": [f"Drug{i}" for i in range(16)]},
        )

    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_analyze_response_has_all_fields(mock_pipeline):
    """Response contains all required fields."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": ["Warfarin", "Aspirin"]},
        )

    data = response.json()
    required_fields = [
        "check_id", "drugs_submitted", "drugs_identified",
        "pairs_checked", "interactions_found", "pairs",
        "overall_severity", "summary", "disclaimer",
        "generated_at", "response_time_ms",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_analyze_disclaimer_always_present(mock_pipeline):
    """Disclaimer always in response."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/analyze-interaction",
            json={"drugs": ["Warfarin", "Aspirin"]},
        )

    data = response.json()
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 20


@pytest.mark.asyncio
async def test_health_endpoint():
    """Health endpoint returns ok."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"