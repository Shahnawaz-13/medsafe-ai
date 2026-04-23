# tests/test_claude_service.py
import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.claude_service import (
    get_interaction_explanations,
    get_chat_response,
    _error_fallback,
)
from app.services.prompt_builder import build_fallback_response
from app.config import settings


# ── Mock Groq response ────────────────────────────────────────────────
MOCK_GROQ_RESPONSE = json.dumps({
    "interactions": [
        {
            "drug1":             "Warfarin",
            "drug2":             "Aspirin",
            "severity":          "high",
            "severity_emoji":    "🔴",
            "plain_explanation": (
                "Warfarin and Aspirin both affect blood clotting. "
                "Taking them together significantly raises your risk "
                "of serious bleeding, including stomach bleeds. "
                "Please consult your doctor or pharmacist immediately "
                "before taking these medications together."
            ),
            "what_to_watch_for": (
                "Unusual bruising or prolonged bleeding from cuts."
            ),
            "action_required":   "Consult your doctor immediately.",
            "safer_alternatives": ["Paracetamol"],
        }
    ],
    "overall_severity": "high",
    "summary":          "1 high-severity interaction found.",
    "disclaimer":       "Educational purposes only.",
})


@pytest.fixture
def sample_pairs():
    return [
        {
            "drug1":            "Warfarin",
            "drug2":            "Aspirin",
            "interaction_text": "Serious bleeding risk.",
            "found":            True,
            "severity":         "high",
            "source":           "OpenFDA",
            "safer_alternatives": ["Paracetamol"],
        }
    ]


def _make_mock_groq_response(content: str):
    """Build a mock Groq API response object."""
    mock_message = MagicMock()
    mock_message.content = content

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_usage = MagicMock()
    mock_usage.prompt_tokens     = 500
    mock_usage.completion_tokens = 200

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage   = mock_usage

    return mock_response


# ── Connection tests ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_connection_success():
    """Test successful Groq connection."""
    mock_response = _make_mock_groq_response(
        "MedSafe AI connected"
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        from app.services.claude_service import test_claude_connection
        result = await test_claude_connection()

    assert result["status"]   == "ok"
    assert result["provider"] == "groq"
    assert result["model"]    == "llama-3.3-70b-versatile"


@pytest.mark.asyncio
async def test_connection_failure():
    """Test connection failure returns error dict."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = (
        Exception("Connection refused")
    )

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        from app.services.claude_service import test_claude_connection
        result = await test_claude_connection()

    assert result["status"] == "error"
    assert "error" in result


# ── Interaction explanation tests ─────────────────────────────────────
@pytest.mark.asyncio
async def test_get_explanations_success(sample_pairs):
    """Test successful Groq response."""
    mock_response = _make_mock_groq_response(MOCK_GROQ_RESPONSE)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_interaction_explanations(sample_pairs)

    assert "interactions"      in result
    assert "overall_severity"  in result
    assert "disclaimer"        in result
    assert result["overall_severity"] == "high"
    assert len(result["interactions"]) == 1
    assert result["interactions"][0]["drug1"] == "Warfarin"
    assert result["interactions"][0]["drug2"] == "Aspirin"


@pytest.mark.asyncio
async def test_get_explanations_with_patient_context(sample_pairs):
    """Test with patient context provided."""
    mock_response = _make_mock_groq_response(MOCK_GROQ_RESPONSE)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_interaction_explanations(
            sample_pairs,
            patient_context={
                "age":       65,
                "gender":    "Male",
                "allergies": ["Penicillin"],
            }
        )

    assert "interactions" in result


@pytest.mark.asyncio
async def test_get_explanations_empty_pairs():
    """Empty pairs returns empty fallback."""
    result = await get_interaction_explanations([])

    assert "interactions" in result
    assert result["interactions"] == []


@pytest.mark.asyncio
async def test_get_explanations_rate_limit(sample_pairs):
    """Rate limit error returns fallback not crash."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = (
        Exception("rate_limit_exceeded: too many requests")
    )

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_interaction_explanations(sample_pairs)

    assert "interactions" in result
    assert "_error"       in result
    assert "rate limit"   in result["_error"].lower()


@pytest.mark.asyncio
async def test_get_explanations_invalid_json(sample_pairs):
    """Invalid JSON from Groq returns fallback."""
    mock_response = _make_mock_groq_response(
        "This is not JSON at all!!!"
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_interaction_explanations(sample_pairs)

    assert "interactions" in result
    assert "_error"       in result


@pytest.mark.asyncio
async def test_get_explanations_has_meta(sample_pairs):
    """Response includes metadata."""
    mock_response = _make_mock_groq_response(MOCK_GROQ_RESPONSE)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_interaction_explanations(sample_pairs)

    assert "_meta"                   in result
    assert result["_meta"]["provider"] == "groq"
    assert "response_time"           in result["_meta"]
    assert "input_tokens"            in result["_meta"]
    assert "output_tokens"           in result["_meta"]


# ── Chat response tests ───────────────────────────────────────────────
@pytest.mark.asyncio
async def test_chat_response_success():
    """Test successful chat response."""
    mock_response = _make_mock_groq_response(
        "Warfarin and ibuprofen have a serious interaction risk."
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_chat_response(
            "Is warfarin safe with ibuprofen?",
            []
        )

    assert isinstance(result, str)
    assert len(result) > 10


@pytest.mark.asyncio
async def test_chat_empty_message():
    """Empty message returns default response."""
    result = await get_chat_response("", [])
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_chat_with_history():
    """Chat includes conversation history."""
    mock_response = _make_mock_groq_response(
        "Given your warfarin use, avoid aspirin for headaches."
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    history = [
        {"role": "user",      "content": "I take warfarin daily."},
        {"role": "assistant", "content": "Noted. Be careful with interactions."},
    ]

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_chat_response(
            "Can I take aspirin?",
            history
        )

    assert isinstance(result, str)

    # Verify history was included in the API call
    call_args = mock_client.chat.completions.create.call_args
    messages  = call_args.kwargs.get(
        "messages",
        call_args.args[0] if call_args.args else []
    )
    assert len(messages) > 2  # system + history + new message


@pytest.mark.asyncio
async def test_chat_error_returns_string():
    """Chat error returns helpful string not exception."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = (
        Exception("Network error")
    )

    with patch(
        "app.services.claude_service._get_client",
        return_value=mock_client
    ):
        result = await get_chat_response("My question", [])

    assert isinstance(result, str)
    assert len(result) > 10


# ── Safety rule tests ─────────────────────────────────────────────────
def test_fallback_never_stops_medication(sample_pairs):
    """Fallback must never tell user to stop medication."""
    result = build_fallback_response(sample_pairs, "Disclaimer")
    for interaction in result["interactions"]:
        explanation = interaction.get("plain_explanation", "").lower()
        assert "stop taking" not in explanation
        assert "stop your"   not in explanation
        assert "discontinue" not in explanation


def test_fallback_always_has_disclaimer(sample_pairs):
    """Disclaimer always present in response."""
    result = build_fallback_response(
        sample_pairs, "Test medical disclaimer"
    )
    assert result["disclaimer"] == "Test medical disclaimer"


def test_fallback_is_flagged(sample_pairs):
    """Fallback response is flagged."""
    result = build_fallback_response(sample_pairs, "Disclaimer")
    assert result.get("fallback") is True


def test_error_fallback_has_error_field(sample_pairs):
    """Error fallback includes error message."""
    result = _error_fallback(sample_pairs, "Test error message")
    assert "_error" in result
    assert result["_error"] == "Test error message"


def test_error_fallback_has_interactions(sample_pairs):
    """Error fallback still has interaction data."""
    result = _error_fallback(sample_pairs, "Test error")
    assert "interactions" in result
    assert len(result["interactions"]) > 0


def test_disclaimer_in_settings():
    """Settings disclaimer is non-empty."""
    assert len(settings.disclaimer) > 50
    assert "consult" in settings.disclaimer.lower()