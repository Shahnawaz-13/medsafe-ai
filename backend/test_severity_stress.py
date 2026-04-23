# test_severity_stress.py (delete after running)
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from app.services.severity_classifier import classify_severity

# 30 real interaction texts with expected severity
TEST_CASES = [
    # CONTRAINDICATED (should return "contraindicated")
    (
        "This combination is absolutely contraindicated.",
        "contraindicated",
        "Warfarin + MAOIs"
    ),
    (
        "Do not use together. Life-threatening reaction possible.",
        "contraindicated",
        "Sildenafil + Nitrates"
    ),
    (
        "Must not be administered concomitantly. Fatal outcome reported.",
        "contraindicated",
        "Pimozide + Clarithromycin"
    ),
    (
        "Avoid combination. Deaths have been reported with this interaction.",
        "contraindicated",
        "Fentanyl + MAOIs"
    ),
    (
        "Never combine these agents under any circumstances.",
        "contraindicated",
        "Linezolid + SSRIs"
    ),

    # HIGH (should return "high")
    (
        "Serious bleeding risk when these drugs are combined.",
        "high",
        "Warfarin + Aspirin"
    ),
    (
        "Severe toxicity has been reported. Close monitoring required.",
        "high",
        "Digoxin + Amiodarone"
    ),
    (
        "Risk of serotonin syndrome. Can be life-altering.",
        "high",
        "Tramadol + SSRIs"
    ),
    (
        "Rhabdomyolysis reported in patients on both medications.",
        "high",
        "Simvastatin + Clarithromycin"
    ),
    (
        "QT prolongation and cardiac arrhythmia risk significantly elevated.",
        "high",
        "Azithromycin + Haloperidol"
    ),
    (
        "Dangerous levels of sedation. Respiratory depression possible.",
        "high",
        "Opioids + Benzodiazepines"
    ),
    (
        "Haemorrhage risk substantially increased with concomitant use.",
        "high",
        "Heparin + NSAIDs"
    ),

    # MODERATE (should return "moderate")
    (
        "Monitor closely. May increase blood glucose levels.",
        "moderate",
        "Steroids + Metformin"
    ),
    (
        "Caution advised. Dosage adjustment may be required.",
        "moderate",
        "Warfarin + Omeprazole"
    ),
    (
        "Reduced efficacy of antihypertensive therapy observed.",
        "moderate",
        "Lisinopril + Aspirin"
    ),
    (
        "Increased risk of hypoglycaemia when taken together.",
        "moderate",
        "Insulin + Alcohol"
    ),
    (
        "Clinically significant interaction. Close monitoring warranted.",
        "moderate",
        "Methotrexate + NSAIDs"
    ),
    (
        "May decrease effectiveness. Use with caution and monitor.",
        "moderate",
        "Antacids + Ciprofloxacin"
    ),
    (
        "Altered drug levels reported. Dosage adjustment recommended.",
        "moderate",
        "Phenytoin + Fluconazole"
    ),

    # LOW (should return "low")
    (
        "Minor interaction with minimal clinical significance expected.",
        "low",
        "Atorvastatin + Amlodipine"
    ),
    (
        "Slight reduction in absorption noted. Generally safe to use.",
        "low",
        "Iron + Vitamin C"
    ),
    (
        "Clinically insignificant. No dose adjustment needed.",
        "low",
        "Metformin + Lisinopril"
    ),
    (
        "Marginal effect on drug levels. Unlikely to cause problems.",
        "low",
        "Omeprazole + Calcium"
    ),

    # NONE (should return "none")
    (
        "No known pharmacokinetic interaction between these agents.",
        "none",
        "Metformin + Atorvastatin"
    ),
    (
        "These drugs act through entirely different pathways.",
        "none",
        "Paracetamol + Metformin"
    ),
    (
        "No clinically relevant interaction has been identified.",
        "none",
        "Lisinopril + Atorvastatin"
    ),
    (
        "Drug interaction studies show no significant findings.",
        "none",
        "Amlodipine + Metformin"
    ),

    # EDGE CASES
    (
        "",
        "none",
        "Empty text"
    ),
    (
        "Take with food. Store below 25 degrees Celsius.",
        "none",
        "General storage instruction"
    ),
    (
        "Patient should be monitored. Some caution is warranted here.",
        "moderate",
        "Ambiguous moderate text"
    ),
]


def run_stress_test():
    print("=" * 65)
    print("Day 10 — Severity Classifier Stress Test (30 cases)")
    print("=" * 65)

    passed = 0
    failed = 0
    results_by_level = {
        "contraindicated": {"pass": 0, "fail": 0},
        "high":            {"pass": 0, "fail": 0},
        "moderate":        {"pass": 0, "fail": 0},
        "low":             {"pass": 0, "fail": 0},
        "none":            {"pass": 0, "fail": 0},
    }

    for i, (text, expected, label) in enumerate(TEST_CASES, 1):
        result = classify_severity(text)
        ok     = result == expected

        status = "✅" if ok else "❌"
        print(
            f"[{i:02d}] {status} {label}"
        )
        if not ok:
            print(
                f"      Expected: {expected.upper()} | "
                f"Got: {result.upper()}"
            )
            print(f"      Text: '{text[:60]}...'")

        if ok:
            passed += 1
            results_by_level[expected]["pass"] += 1
        else:
            failed += 1
            results_by_level[expected]["fail"] += 1

    accuracy = round(passed / len(TEST_CASES) * 100, 1)

    print("\n" + "=" * 65)
    print(f"Results: {passed}/{len(TEST_CASES)} correct ({accuracy}%)")
    print("\nBy severity level:")
    for level, counts in results_by_level.items():
        total = counts["pass"] + counts["fail"]
        if total > 0:
            pct = round(counts["pass"] / total * 100)
            print(
                f"  {level.upper():>15}: "
                f"{counts['pass']}/{total} ({pct}%)"
            )

    print()
    if accuracy >= 85:
        print(f"✅ Stress test PASSED — {accuracy}% accuracy")
    elif accuracy >= 70:
        print(f"⚠️  Stress test MARGINAL — {accuracy}% accuracy")
        print("   Add more keyword patterns for failed cases")
    else:
        print(f"❌ Stress test FAILED — {accuracy}% accuracy")
        print("   Review classifier logic")
    print("=" * 65)


run_stress_test()