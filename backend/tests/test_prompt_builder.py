# tests/test_prompt_builder.py
import pytest
import json
from app.services.prompt_builder import (
    build_analysis_prompt,
    build_chat_prompt,
    validate_claude_response,
    build_fallback_response,
    SYSTEM_PROMPT,
)
from app.config import settings


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
        },
        {
            "drug1":            "Metformin",
            "drug2":            "Lisinopril",
            "interaction_text": "",
            "found":            False,
            "severity":         "none",
            "source":           "OpenFDA",
            "safer_alternatives": [],
        },
    ]


@pytest.fixture
def valid_claude_response():
    return json.dumps({
        "interactions": [
            {
                "drug1":             "Warfarin",
                "drug2":             "Aspirin",
                "severity":          "high",
                "severity_emoji":    "🔴",
                "plain_explanation": "This is a serious interaction.",
                "what_to_watch_for": "Watch for bleeding.",
                "action_required":   "See your doctor.",
                "safer_alternatives": ["Paracetamol"],
            }
        ],
        "overall_severity": "high",
        "summary":          "1 high interaction found.",
        "disclaimer":       "Educational purposes only.",
    })


# ── Prompt building tests ─────────────────────────────────────────────
def test_prompt_contains_drug_names(sample_pairs):
    prompt = build_analysis_prompt(sample_pairs)
    assert "Warfarin" in prompt
    assert "Aspirin" in prompt
    assert "Metformin" in prompt


def test_prompt_contains_interaction_text(sample_pairs):
    prompt = build_analysis_prompt(sample_pairs)
    assert "bleeding risk" in prompt


def test_prompt_is_string(sample_pairs):
    prompt = build_analysis_prompt(sample_pairs)
    assert isinstance(prompt, str)
    assert len(prompt) > 100


def test_prompt_with_patient_context(sample_pairs):
    prompt = build_analysis_prompt(
        sample_pairs,
        patient_context={"age": 65, "gender": "Male"}
    )
    assert "65" in prompt
    assert "Male" in prompt


def test_prompt_without_context_has_no_patient_section(sample_pairs):
    prompt = build_analysis_prompt(sample_pairs)
    assert "PATIENT CONTEXT" not in prompt


def test_system_prompt_has_never_fabricate():
    assert "NEVER fabricate" in SYSTEM_PROMPT


def test_system_prompt_has_never_diagnose():
    assert "NEVER diagnose" in SYSTEM_PROMPT


def test_system_prompt_has_json_rule():
    assert "valid JSON" in SYSTEM_PROMPT


def test_system_prompt_has_all_severity_levels():
    for level in ["low", "moderate", "high", "contraindicated", "none"]:
        assert level in SYSTEM_PROMPT


# ── Chat prompt tests ─────────────────────────────────────────────────
def test_chat_prompt_includes_user_message():
    messages = build_chat_prompt("Is aspirin safe?", [])
    last_msg  = messages[-1]
    assert last_msg["role"] == "user"
    assert "aspirin" in last_msg["content"].lower()


def test_chat_prompt_includes_history():
    history = [
        {"role": "user",      "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    messages = build_chat_prompt("My question", history)
    assert len(messages) == 3


def test_chat_prompt_limits_history():
    history = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(20)
    ]
    messages = build_chat_prompt("New question", history)
    assert len(messages) <= 11  # 10 history + 1 current


# ── Validate response tests ───────────────────────────────────────────
def test_validates_correct_response(valid_claude_response):
    result = validate_claude_response(valid_claude_response)
    assert "interactions" in result
    assert "overall_severity" in result
    assert result["overall_severity"] == "high"


def test_strips_markdown_fences(valid_claude_response):
    fenced = f"```json\n{valid_claude_response}\n```"
    result = validate_claude_response(fenced)
    assert "interactions" in result


def test_raises_on_invalid_json():
    with pytest.raises(ValueError):
        validate_claude_response("not valid json {{")


def test_raises_on_missing_interactions():
    bad = json.dumps({"overall_severity": "high"})
    with pytest.raises(ValueError):
        validate_claude_response(bad)


def test_fixes_invalid_severity(valid_claude_response):
    data = json.loads(valid_claude_response)
    data["interactions"][0]["severity"] = "INVALID"
    result = validate_claude_response(json.dumps(data))
    assert result["interactions"][0]["severity"] == "none"


# ── Fallback response tests ───────────────────────────────────────────
def test_fallback_has_all_pairs(sample_pairs):
    result = build_fallback_response(sample_pairs, "Disclaimer")
    assert len(result["interactions"]) == len(sample_pairs)


def test_fallback_is_flagged(sample_pairs):
    result = build_fallback_response(sample_pairs, "Disclaimer")
    assert result.get("fallback") is True


def test_fallback_has_disclaimer(sample_pairs):
    result = build_fallback_response(
        sample_pairs, "Test disclaimer"
    )
    assert result["disclaimer"] == "Test disclaimer"