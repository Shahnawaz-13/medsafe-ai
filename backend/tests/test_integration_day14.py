# tests/test_integration_day14.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from main import app


# ── Full pipeline integration tests ──────────────────────────────────
@pytest.mark.asyncio
async def test_full_api_pipeline():
    """Test complete API pipeline returns valid response."""
    mock_normalized = [
        {"input_name": "Warfarin",  "normalized_name": "Warfarin",
         "rxcui": "11289", "found": True},
        {"input_name": "Aspirin",   "normalized_name": "Aspirin",
         "rxcui": "1191",  "found": True},
        {"input_name": "Metformin", "normalized_name": "Metformin",
         "rxcui": "6809",  "found": True},
    ]

    mock_resolved = [
        {"drug1": "Warfarin", "drug2": "Aspirin",
         "interaction_text": "Serious bleeding risk.",
         "found": True, "severity": "high",
         "from_cache": False, "source": "OpenFDA",
         "safer_alternatives": ["Paracetamol"]},
        {"drug1": "Warfarin", "drug2": "Metformin",
         "interaction_text": "",
         "found": False, "severity": "none",
         "from_cache": False, "source": "OpenFDA",
         "safer_alternatives": []},
        {"drug1": "Aspirin",  "drug2": "Metformin",
         "interaction_text": "",
         "found": False, "severity": "none",
         "from_cache": False, "source": "OpenFDA",
         "safer_alternatives": []},
    ]

    mock_ai = {
        "interactions": [
            {
                "drug1": "Warfarin", "drug2": "Aspirin",
                "severity": "high", "severity_emoji": "🔴",
                "plain_explanation": (
                    "Warfarin and Aspirin both thin your blood. "
                    "Together they raise your bleeding risk seriously. "
                    "Consult your doctor immediately."
                ),
                "what_to_watch_for": "Unusual bruising.",
                "action_required":   "See your doctor.",
                "safer_alternatives": ["Paracetamol"],
                "mechanism": "", "sources": [],
            },
            {
                "drug1": "Warfarin", "drug2": "Metformin",
                "severity": "none", "severity_emoji": "⚪",
                "plain_explanation": "No known interaction detected.",
                "what_to_watch_for": "",
                "action_required":   "No action needed.",
                "safer_alternatives": [],
                "mechanism": "", "sources": [],
            },
            {
                "drug1": "Aspirin", "drug2": "Metformin",
                "severity": "none", "severity_emoji": "⚪",
                "plain_explanation": "No known interaction detected.",
                "what_to_watch_for": "",
                "action_required":   "No action needed.",
                "safer_alternatives": [],
                "mechanism": "", "sources": [],
            },
        ],
        "overall_severity": "high",
        "summary":          "1 high-severity interaction found.",
        "disclaimer":       "Educational purposes only.",
    }

    with patch(
        "app.routers.analyze.normalize_drug_list",
        new_callable=AsyncMock,
        return_value=mock_normalized,
    ), patch(
        "app.routers.analyze.resolve_all_pairs",
        new_callable=AsyncMock,
        return_value=mock_resolved,
    ), patch(
        "app.routers.analyze.get_interaction_explanations",
        new_callable=AsyncMock,
        return_value=mock_ai,
    ), patch(
        "app.routers.analyze.get_db",
        return_value=None,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze-interaction",
                json={
                    "drugs":  ["Warfarin", "Aspirin", "Metformin"],
                    "age":    65,
                    "gender": "Male",
                },
            )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert data["drugs_submitted"]    == 3
    assert data["drugs_identified"]   == 3
    assert data["pairs_checked"]      == 3
    assert data["interactions_found"] == 1
    assert data["overall_severity"]   == "high"
    assert data["overall_emoji"]      == "🔴"
    assert len(data["pairs"])         == 3
    assert "disclaimer"               in data
    assert "check_id"                 in data
    assert "response_time_ms"         in data


@pytest.mark.asyncio
async def test_pipeline_all_no_interactions():
    """Pipeline with no interactions returns overall=none."""
    mock_normalized = [
        {"input_name": "Metformin",  "normalized_name": "Metformin",
         "rxcui": "6809",  "found": True},
        {"input_name": "Lisinopril", "normalized_name": "Lisinopril",
         "rxcui": "29046", "found": True},
    ]

    mock_resolved = [
        {"drug1": "Metformin", "drug2": "Lisinopril",
         "interaction_text": "", "found": False,
         "severity": "none", "from_cache": False,
         "source": "OpenFDA", "safer_alternatives": []},
    ]

    mock_ai = {
        "interactions": [
            {
                "drug1": "Metformin", "drug2": "Lisinopril",
                "severity": "none", "severity_emoji": "⚪",
                "plain_explanation": "No known interaction.",
                "what_to_watch_for": "",
                "action_required":   "No action needed.",
                "safer_alternatives": [],
                "mechanism": "", "sources": [],
            }
        ],
        "overall_severity": "none",
        "summary":          "No interactions found.",
        "disclaimer":       "Educational purposes only.",
    }

    with patch(
        "app.routers.analyze.normalize_drug_list",
        new_callable=AsyncMock, return_value=mock_normalized,
    ), patch(
        "app.routers.analyze.resolve_all_pairs",
        new_callable=AsyncMock, return_value=mock_resolved,
    ), patch(
        "app.routers.analyze.get_interaction_explanations",
        new_callable=AsyncMock, return_value=mock_ai,
    ), patch(
        "app.routers.analyze.get_db", return_value=None,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze-interaction",
                json={"drugs": ["Metformin", "Lisinopril"]},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["overall_severity"]   == "none"
    assert data["overall_emoji"]      == "⚪"
    assert data["interactions_found"] == 0


@pytest.mark.asyncio
async def test_pipeline_disclaimer_never_missing():
    """Disclaimer is always present no matter what."""
    mock_normalized = [
        {"input_name": "DrugA", "normalized_name": "DrugA",
         "rxcui": "111", "found": True},
        {"input_name": "DrugB", "normalized_name": "DrugB",
         "rxcui": "222", "found": True},
    ]

    mock_resolved = [
        {"drug1": "DrugA", "drug2": "DrugB",
         "interaction_text": "", "found": False,
         "severity": "none", "from_cache": False,
         "source": "OpenFDA", "safer_alternatives": []},
    ]

    # AI response WITHOUT disclaimer
    mock_ai_no_disclaimer = {
        "interactions":     [],
        "overall_severity": "none",
        "summary":          "No interactions.",
        # No disclaimer field
    }

    with patch(
        "app.routers.analyze.normalize_drug_list",
        new_callable=AsyncMock, return_value=mock_normalized,
    ), patch(
        "app.routers.analyze.resolve_all_pairs",
        new_callable=AsyncMock, return_value=mock_resolved,
    ), patch(
        "app.routers.analyze.get_interaction_explanations",
        new_callable=AsyncMock, return_value=mock_ai_no_disclaimer,
    ), patch(
        "app.routers.analyze.get_db", return_value=None,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze-interaction",
                json={"drugs": ["DrugA", "DrugB"]},
            )

    assert response.status_code == 200
    data = response.json()
    # Disclaimer must ALWAYS be present
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 20


@pytest.mark.asyncio
async def test_swagger_docs_accessible():
    """Swagger UI is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_all_routes_exist():
    """All API routes return something (not 404)."""
    routes_to_check = [
        ("GET",  "/health"),
        ("GET",  "/health/simple"),
        ("GET",  "/"),
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        for method, path in routes_to_check:
            if method == "GET":
                response = await client.get(path)
            assert response.status_code != 404, (
                f"Route {method} {path} returned 404"
            )


@pytest.mark.asyncio
async def test_cors_headers_present():
    """CORS headers are present in response."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.options(
            "/api/analyze-interaction",
            headers={"Origin": "http://localhost:3000"},
        )
    # CORS preflight should not 404
    assert response.status_code != 404


# ── Week 2 completion verification ───────────────────────────────────
def test_all_services_importable():
    """All services can be imported without errors."""
    from app.services.normaliser          import normalize_drug_list
    from app.services.pair_generator      import generate_pairs
    from app.services.interaction_resolver import resolve_all_pairs
    from app.services.alternative_service import get_alternatives_for_pairs
    from app.services.claude_service      import get_interaction_explanations
    from app.services.severity_classifier import classify_severity
    from app.services.cache_service       import get_cache_stats
    from app.services.prompt_builder      import build_analysis_prompt
    assert True


def test_all_routers_importable():
    """All routers can be imported without errors."""
    from app.routers.analyze  import router as analyze_router
    from app.routers.drug_info import router as drug_info_router
    from app.routers.chat     import router as chat_router
    from app.routers.history  import router as history_router
    from app.routers.upload   import router as upload_router
    from app.routers.health   import router as health_router
    assert True


def test_config_has_all_required_fields():
    """Config has all required fields."""
    from app.config import settings
    assert hasattr(settings, "groq_api_key")
    assert hasattr(settings, "mongodb_uri")
    assert hasattr(settings, "rxnorm_base_url")
    assert hasattr(settings, "openfda_api_key")
    assert hasattr(settings, "disclaimer")
    assert hasattr(settings, "max_drugs_per_request")
    assert len(settings.disclaimer) > 50