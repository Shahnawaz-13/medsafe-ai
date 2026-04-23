# tests/conftest.py
import pytest
import asyncio
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_drugs():
    """Standard drug list for testing."""
    return [
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
        {
            "input_name":      "Metformin",
            "normalized_name": "Metformin",
            "rxcui":           "6809",
            "found":           True,
        },
        {
            "input_name":      "Lisinopril",
            "normalized_name": "Lisinopril",
            "rxcui":           "29046",
            "found":           True,
        },
    ]


@pytest.fixture
def sample_interaction_text_high():
    return (
        "Serious risk of bleeding. Avoid combination unless "
        "benefits outweigh risks. Monitor closely."
    )


@pytest.fixture
def sample_interaction_text_contraindicated():
    return (
        "Contraindicated. Do not use together under any "
        "circumstances. Life-threatening reaction possible."
    )


@pytest.fixture
def sample_interaction_result():
    return {
        "drug1":            "Warfarin",
        "drug2":            "Aspirin",
        "severity":         "high",
        "severity_emoji":   "🔴",
        "plain_explanation": (
            "Both Warfarin and Aspirin affect your blood's "
            "ability to clot. Taking them together significantly "
            "raises your risk of serious bleeding."
        ),
        "what_to_watch_for": (
            "Unusual bruising, blood in urine or stool, "
            "prolonged bleeding from cuts."
        ),
        "action_required": (
            "Consult your doctor immediately before taking "
            "these together."
        ),
        "safer_alternatives": ["Paracetamol"],
        "mechanism":         "Pharmacodynamic synergy",
        "sources":           ["OpenFDA"],
    }