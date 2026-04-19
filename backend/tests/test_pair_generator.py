# tests/test_pair_generator.py
import pytest
from app.services.pair_generator import (
    generate_pairs,
    get_pair_count
)


def make_drug(name, rxcui):
    return {
        "input_name": name,
        "normalized_name": name,
        "rxcui": rxcui,
    }


def test_four_drugs_six_pairs():
    drugs = [
        make_drug("Warfarin",   "11289"),
        make_drug("Aspirin",    "1191"),
        make_drug("Metformin",  "6809"),
        make_drug("Lisinopril", "29046"),
    ]
    pairs = generate_pairs(drugs)
    assert len(pairs) == 6


def test_two_drugs_one_pair():
    drugs = [
        make_drug("Warfarin", "11289"),
        make_drug("Aspirin",  "1191"),
    ]
    pairs = generate_pairs(drugs)
    assert len(pairs) == 1


def test_single_drug_no_pairs():
    drugs = [make_drug("Warfarin", "11289")]
    pairs = generate_pairs(drugs)
    assert len(pairs) == 0


def test_pair_count_formula():
    assert get_pair_count(2)  == 1
    assert get_pair_count(3)  == 3
    assert get_pair_count(4)  == 6
    assert get_pair_count(5)  == 10
    assert get_pair_count(10) == 45


def test_filters_both_no_rxcui():
    drugs = [
        make_drug("Unknown1", None),
        make_drug("Unknown2", None),
        make_drug("Warfarin", "11289"),
    ]
    pairs = generate_pairs(drugs)
    # Unknown1+Unknown2 skipped; others kept
    assert len(pairs) == 2