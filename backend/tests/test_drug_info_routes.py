# tests/test_drug_info_routes.py
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from main import app


MOCK_NORMALIZE_FOUND = {
    "input_name":      "Warfarin",
    "normalized_name": "Warfarin",
    "rxcui":           "11289",
    "found":           True,
}

MOCK_NORMALIZE_NOT_FOUND = {
    "input_name":      "xyzfake",
    "normalized_name": "xyzfake",
    "rxcui":           None,
    "found":           False,
}

MOCK_AUTOCOMPLETE_RESPONSE = {
    "approximateGroup": {
        "candidate": [
            {"rxcui": "11289", "name": "Warfarin", "score": 100},
            {"rxcui": "11290", "name": "Warfarin Sodium", "score": 90},
        ]
    }
}


# ── Drug info tests ───────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_drug_info_found():
    """Known drug returns 200 with rxcui."""
    with patch(
        "app.routers.drug_info.normalize_drug_name",
        new_callable=AsyncMock,
        return_value=MOCK_NORMALIZE_FOUND,
    ), patch(
        "app.routers.drug_info._get_drug_class",
        new_callable=AsyncMock,
        return_value="Anticoagulant",
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-info?name=Warfarin"
            )

    assert response.status_code == 200
    data = response.json()
    assert data["found"]   is True
    assert data["rxcui"]   == "11289"
    assert "canonical_name" in data


@pytest.mark.asyncio
async def test_drug_info_not_found():
    """Unknown drug returns 404."""
    with patch(
        "app.routers.drug_info.normalize_drug_name",
        new_callable=AsyncMock,
        return_value=MOCK_NORMALIZE_NOT_FOUND,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-info?name=xyzfake"
            )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_drug_info_too_short():
    """Single character returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/drug-info?name=a")

    assert response.status_code == 422


# ── Autocomplete tests ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_autocomplete_returns_suggestions():
    """Autocomplete returns list of suggestions."""
    import httpx as httpx_module
    from unittest.mock import MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_AUTOCOMPLETE_RESPONSE

    with patch(
        "httpx.AsyncClient.get",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-autocomplete?q=war"
            )

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


@pytest.mark.asyncio
async def test_autocomplete_too_short():
    """Single character query returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/drug-autocomplete?q=a"
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_autocomplete_empty_on_error():
    """API error returns empty suggestions not crash."""
    with patch(
        "httpx.AsyncClient.get",
        side_effect=Exception("Network error")
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-autocomplete?q=war"
            )

    assert response.status_code == 200
    assert response.json()["suggestions"] == []


# ── Drug validate tests ───────────────────────────────────────────────
@pytest.mark.asyncio
async def test_validate_known_drug():
    """Known drug returns valid=True."""
    with patch(
        "app.routers.drug_info.normalize_drug_name",
        new_callable=AsyncMock,
        return_value=MOCK_NORMALIZE_FOUND,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-validate?name=Warfarin"
            )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["rxcui"] == "11289"


@pytest.mark.asyncio
async def test_validate_unknown_drug():
    """Unknown drug returns valid=False."""
    with patch(
        "app.routers.drug_info.normalize_drug_name",
        new_callable=AsyncMock,
        return_value=MOCK_NORMALIZE_NOT_FOUND,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/drug-validate?name=xyzfake"
            )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


# ── Chat route tests ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_chat_success():
    """Chat returns reply string."""
    with patch(
        "app.routers.chat.get_chat_response",
        new_callable=AsyncMock,
        return_value="Warfarin and ibuprofen have a serious interaction.",
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/chat",
                json={"message": "Is warfarin safe with ibuprofen?"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "reply"     in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_chat_empty_message():
    """Empty message returns 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/chat",
            json={"message": ""},
        )

    assert response.status_code in [400, 422]