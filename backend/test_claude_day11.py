# test_claude_day11.py (delete after running)
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from app.services.claude_service import (
    get_interaction_explanations,
    get_chat_response,
    test_claude_connection,
)
from app.services.severity_classifier import get_severity_emoji


async def test():
    print("=" * 65)
    print("Day 11 — Groq AI Integration Test")
    print("=" * 65)

    # ── Test 1: Connection ────────────────────────────────────────────
    print("\n[1] Testing Groq API connection...")
    result = await test_claude_connection()

    if result["status"] == "ok":
        print(f"    ✅ Connected!")
        print(f"    Provider : {result['provider']}")
        print(f"    Model    : {result['model']}")
        print(f"    Reply    : '{result['reply']}'")
    else:
        print(f"    ❌ Connection failed: {result['error']}")
        print(
            "    Fix: Check GROQ_API_KEY in .env\n"
            "    Get free key: https://console.groq.com"
        )
        return

    # ── Test 2: Drug Interaction Explanation ──────────────────────────
    print("\n[2] Testing drug interaction explanation...")
    print("    Drugs: Warfarin + Aspirin | Metformin + Lisinopril")

    sample_pairs = [
        {
            "drug1": "Warfarin",
            "drug2": "Aspirin",
            "interaction_text": (
                "Warfarin sodium and aspirin, when used together, "
                "have a serious drug interaction. Aspirin can "
                "displace warfarin from protein binding sites and "
                "also inhibits platelet aggregation, significantly "
                "increasing the risk of serious haemorrhage. "
                "Avoid unless the benefit outweighs the serious risk."
            ),
            "found":             True,
            "severity":          "high",
            "source":            "OpenFDA Label",
            "safer_alternatives": ["Paracetamol", "Celecoxib"],
        },
        {
            "drug1":             "Metformin",
            "drug2":             "Lisinopril",
            "interaction_text":  "",
            "found":             False,
            "severity":          "none",
            "source":            "OpenFDA",
            "safer_alternatives": [],
        },
    ]

    print("\n    Calling Groq API...")
    result = await get_interaction_explanations(
        sample_pairs,
        patient_context={"age": 65, "gender": "Male"},
    )

    # Check fallback
    if result.get("_error"):
        print(f"\n    ⚠️  Fallback: {result['_error']}")
    else:
        print(f"\n    ✅ AI response received!")

    # Overall severity
    overall       = result.get("overall_severity", "none")
    overall_emoji = get_severity_emoji(overall)
    print(f"    Overall   : {overall.upper()} {overall_emoji}")
    print(f"    Summary   : {result.get('summary', 'N/A')}")

    # Per-pair results
    print(f"\n    Results:")
    print("    " + "-" * 55)

    interactions = result.get("interactions", [])
    for i, interaction in enumerate(interactions, 1):
        emoji = interaction.get("severity_emoji", "⚪")
        sev   = interaction.get("severity", "none").upper()
        d1    = interaction.get("drug1", "Unknown")
        d2    = interaction.get("drug2", "Unknown")

        print(f"\n    [{i}] {emoji} {d1} + {d2} — {sev}")

        explanation = interaction.get("plain_explanation", "")
        if explanation:
            print(
                f"         Explanation  : "
                f"{explanation[:150]}..."
            )

        watch = interaction.get("what_to_watch_for", "")
        if watch:
            print(f"         Watch for    : {watch}")

        action = interaction.get("action_required", "")
        if action:
            print(f"         Action       : {action}")

        alts = interaction.get("safer_alternatives", [])
        if alts:
            print(f"         Alternatives : {', '.join(alts)}")

    # Metadata
    print("\n    " + "-" * 55)
    if "_meta" in result:
        meta = result["_meta"]
        print(f"    Provider      : {meta.get('provider', 'groq')}")
        print(f"    Model         : {meta.get('model', 'N/A')}")
        print(
            f"    Response time : "
            f"{meta.get('response_time', 'N/A')}s"
        )
        if meta.get("input_tokens"):
            print(
                f"    Tokens        : "
                f"in={meta['input_tokens']}, "
                f"out={meta['output_tokens']}"
            )

    # ── Test 3: Safety Rules ──────────────────────────────────────────
    print("\n[3] Verifying AI safety rules...")

    if not interactions:
        print("    ⚠️  No interactions — skipping safety checks")
        all_passed = False
    else:
        explanation = interactions[0].get("plain_explanation", "")

        safety_checks = [
            (
                "stop taking" not in explanation.lower(),
                "Does NOT tell user to stop medication"
            ),
            (
                "stop your" not in explanation.lower(),
                "Does NOT say stop your medication"
            ),
            (
                "diagnos" not in explanation.lower(),
                "Does NOT diagnose conditions"
            ),
            (
                len(explanation) >= 50,
                f"Min length met ({len(explanation)} chars)"
            ),
            (
                len(explanation) <= 700,
                f"Max length met ({len(explanation)} chars)"
            ),
            (
                "disclaimer" in result,
                "Disclaimer always included"
            ),
            (
                result.get("overall_severity") in [
                    "low", "moderate", "high",
                    "contraindicated", "none"
                ],
                "Overall severity is valid"
            ),
        ]

        all_passed = True
        for check_passed, check_name in safety_checks:
            status = "✅" if check_passed else "❌"
            print(f"    {status} {check_name}")
            if not check_passed:
                all_passed = False

    # ── Test 4: RxChat ────────────────────────────────────────────────
    print("\n[4] Testing RxChat conversational AI...")

    questions = [
        "Can I take ibuprofen with warfarin?",
        "Is it safe to drink alcohol with metformin?",
    ]

    chat_passed = True
    for question in questions:
        print(f"\n    Q: {question}")
        chat_response = await get_chat_response(question, [])
        if chat_response and len(chat_response) > 10:
            print(f"    ✅ ({len(chat_response)} chars)")
            print(f"    A: {chat_response[:150]}...")
        else:
            print("    ❌ Empty response")
            chat_passed = False

    # ── Test 5: Multi-turn Chat ───────────────────────────────────────
    print("\n[5] Testing multi-turn conversation...")

    history = [
        {
            "role":    "user",
            "content": "I take warfarin daily.",
        },
        {
            "role":    "assistant",
            "content": (
                "I understand. Warfarin requires careful "
                "monitoring for drug interactions."
            ),
        },
    ]

    followup = await get_chat_response(
        "Can I take aspirin for a headache?",
        history
    )

    if followup and len(followup) > 10:
        print(f"    ✅ Multi-turn response received")
        print(f"    Response: {followup[:180]}...")
    else:
        print("    ❌ Multi-turn chat failed")

    # ── Final Verdict ─────────────────────────────────────────────────
    print("\n" + "=" * 65)

    has_error   = bool(result.get("_error"))
    is_fallback = result.get("fallback", False)

    if not has_error and not is_fallback and all_passed and chat_passed:
        print("✅ ALL TESTS PASSED")
        print("   Provider  : Groq (LLaMA 3.3 70B)")
        print("   Status    : MedSafe AI is now intelligent")
        print("   Next step : Day 12 — POST /analyze-interaction")
    elif has_error or is_fallback:
        print("⚠️  AI FALLBACK ACTIVE")
        print(f"   Error  : {result.get('_error', 'Unknown')}")
        print("   Action : Check GROQ_API_KEY in .env")
        print("   Key    : https://console.groq.com")
    else:
        print("⚠️  SOME CHECKS FAILED — review output above")

    print("=" * 65)


asyncio.run(test())