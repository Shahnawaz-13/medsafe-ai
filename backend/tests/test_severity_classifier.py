# tests/test_severity_classifier.py
import pytest
from app.services.severity_classifier import (
    classify_severity,
    get_severity_emoji,
    get_overall_severity,
)


def test_contraindicated_keyword():
    text = "This combination is contraindicated in all patients."
    assert classify_severity(text) == "contraindicated"


def test_high_keyword():
    text = "There is a serious risk of bleeding when combined."
    assert classify_severity(text) == "high"


def test_moderate_keyword():
    text = "Monitor closely as may increase blood pressure levels."
    assert classify_severity(text) == "moderate"


def test_low_keyword():
    text = "Minor interaction with minimal clinical significance."
    assert classify_severity(text) == "low"


def test_no_keyword():
    text = "These two drugs work through different pathways."
    assert classify_severity(text) == "none"


def test_empty_text():
    assert classify_severity("") == "none"
    assert classify_severity(None) == "none"


def test_priority_order():
    """Contraindicated beats high if both keywords present."""
    text = "Contraindicated. Serious bleeding risk also present."
    assert classify_severity(text) == "contraindicated"


def test_get_severity_emoji():
    assert get_severity_emoji("contraindicated") == "🚫"
    assert get_severity_emoji("high")            == "🔴"
    assert get_severity_emoji("moderate")        == "🟡"
    assert get_severity_emoji("low")             == "🟢"
    assert get_severity_emoji("none")            == "⚪"


def test_get_overall_severity_highest_wins():
    severities = ["low", "high", "moderate", "none"]
    assert get_overall_severity(severities) == "high"


def test_get_overall_severity_contraindicated():
    severities = ["high", "contraindicated", "moderate"]
    assert get_overall_severity(severities) == "contraindicated"


def test_get_overall_severity_all_none():
    assert get_overall_severity(["none", "none"]) == "none"