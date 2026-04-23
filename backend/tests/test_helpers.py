# tests/test_helpers.py
import pytest
from app.utils.helpers import (
    generate_session_id,
    generate_pair_key,
    sanitize_drug_name,
    format_timestamp,
    chunk_list,
)


def test_session_id_is_unique():
    id1 = generate_session_id()
    id2 = generate_session_id()
    assert id1 != id2
    assert len(id1) == 36   # UUID format


def test_pair_key_is_order_independent():
    """Same pair in different order must give same key."""
    key1 = generate_pair_key("11289", "1191")
    key2 = generate_pair_key("1191", "11289")
    assert key1 == key2


def test_pair_key_different_pairs_differ():
    key1 = generate_pair_key("11289", "1191")
    key2 = generate_pair_key("11289", "6809")
    assert key1 != key2


def test_sanitize_removes_special_chars():
    result = sanitize_drug_name("War<farin>!")
    assert "<" not in result
    assert ">" not in result
    assert "!" not in result


def test_sanitize_strips_whitespace():
    result = sanitize_drug_name("  Warfarin  ")
    assert result == "Warfarin"


def test_sanitize_empty_string():
    assert sanitize_drug_name("") == ""
    assert sanitize_drug_name(None) == ""


def test_sanitize_length_limit():
    long_name = "A" * 200
    result    = sanitize_drug_name(long_name)
    assert len(result) <= 100


def test_format_timestamp_returns_string():
    ts = format_timestamp()
    assert isinstance(ts, str)
    assert ts.endswith("Z")


def test_chunk_list():
    lst    = [1, 2, 3, 4, 5, 6, 7]
    chunks = chunk_list(lst, 3)
    assert len(chunks) == 3
    assert chunks[0] == [1, 2, 3]
    assert chunks[2] == [7]