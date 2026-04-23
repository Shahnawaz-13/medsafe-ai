# test_prompt_builder.py (delete after)
import json
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from app.services.prompt_builder import (
    build_analysis_prompt,
    validate_claude_response,
    build_fallback_response,
    SYSTEM_PROMPT,
    EXPECTED_FORMAT,
)
from app.config import settings


def test_prompt_builder():
    print("=" * 65)
    print("Day 10 — Prompt Builder Validation")
    print("=" * 65)

    # Sample pairs (as if from OpenFDA resolver)
    sample_pairs = [
        {
            "drug1":            "Warfarin",
            "drug2":            "Aspirin",
            "interaction_text": (
                "Serious bleeding risk. Warfarin's anticoagulant "
                "effect is significantly enhanced by aspirin. "
                "Avoid unless benefits outweigh risks."
            ),
            "found":    True,
            "severity": "high",
            "source":   "OpenFDA Label",
            "safer_alternatives": ["Paracetamol"],
        },
        {
            "drug1":            "Metformin",
            "drug2":            "Lisinopril",
            "interaction_text": "",
            "found":    False,
            "severity": "none",
            "source":   "OpenFDA",
            "safer_alternatives": [],
        },
    ]

    # Test 1: Prompt builds correctly
    prompt = build_analysis_prompt(sample_pairs)
    print(f"\n[1] Prompt built successfully")
    print(f"    Length: {len(prompt)} characters")
    print(f"    Contains drug names: "
          f"{'Warfarin' in prompt and 'Aspirin' in prompt}")
    print(f"    Contains interaction text: "
          f"{'bleeding risk' in prompt}")

    # Test 2: System prompt has all 15 rules
    rule_count = sum(
        1 for i in range(1, 16)
        if str(i) + "." in SYSTEM_PROMPT
    )
    print(f"\n[2] System prompt: {rule_count}/15 rules present")
    print(f"    Length: {len(SYSTEM_PROMPT)} characters")

    # Test 3: Expected format is valid JSON
    try:
        json.dumps(EXPECTED_FORMAT)
        print(f"\n[3] Expected format is valid JSON ✅")
    except Exception as e:
        print(f"\n[3] Expected format JSON error: {e} ❌")

    # Test 4: Validate a correct mock response
    mock_response = json.dumps({
        "interactions": [
            {
                "drug1":             "Warfarin",
                "drug2":             "Aspirin",
                "severity":          "high",
                "severity_emoji":    "🔴",
                "plain_explanation": (
                    "Warfarin and Aspirin both affect how your blood "
                    "clots. Taking them together significantly raises "
                    "your risk of serious bleeding, including stomach "
                    "bleeds. Please consult your doctor or pharmacist "
                    "immediately before taking these medications together."
                ),
                "what_to_watch_for": (
                    "Unusual bruising, blood in urine, or prolonged "
                    "bleeding from cuts."
                ),
                "action_required": (
                    "Consult your doctor immediately."
                ),
                "safer_alternatives": ["Paracetamol"],
            }
        ],
        "overall_severity": "high",
        "summary": (
            "1 high-severity interaction found. Please review carefully."
        ),
        "disclaimer": (
            "MedSafe AI provides educational information only."
        ),
    })

    try:
        validated = validate_claude_response(mock_response)
        print(f"\n[4] Mock response validated ✅")
        print(
            f"    Interactions: {len(validated['interactions'])}"
        )
        print(f"    Overall: {validated['overall_severity']}")
    except Exception as e:
        print(f"\n[4] Validation error: {e} ❌")

    # Test 5: Fallback response
    fallback = build_fallback_response(sample_pairs, settings.disclaimer)
    print(f"\n[5] Fallback response built ✅")
    print(f"    Interactions: {len(fallback['interactions'])}")
    print(f"    Is fallback: {fallback.get('fallback', False)}")

    # Test 6: Patient context
    prompt_with_context = build_analysis_prompt(
        sample_pairs,
        patient_context={
            "age":        65,
            "gender":     "Male",
            "allergies":  ["Penicillin"],
            "conditions": ["diabetes", "hypertension"],
        }
    )
    print(f"\n[6] Prompt with patient context ✅")
    print(f"    Contains age: {'age: 65' in prompt_with_context}")
    print(
        f"    Contains allergies: "
        f"{'Penicillin' in prompt_with_context}"
    )

    # Test 7: Validate handles markdown fences
    with_fences = "```json\n" + mock_response + "\n```"
    try:
        validated2 = validate_claude_response(with_fences)
        print(f"\n[7] Markdown fence stripping works ✅")
    except Exception as e:
        print(f"\n[7] Fence stripping failed: {e} ❌")

    print("\n" + "=" * 65)
    print("✅ Prompt builder validation COMPLETE")
    print("=" * 65)


test_prompt_builder()