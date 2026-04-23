# app/services/prompt_builder.py
import json
import logging
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT — Immutable. Never modified by user input.
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are MedSafe AI, a medical information assistant
specialised in drug interaction analysis. Your role is to take raw
pharmacological interaction data and translate it into clear, accurate,
and compassionate explanations for non-medical users.

STRICT RULES — FOLLOW EVERY RULE WITHOUT EXCEPTION:

1. NEVER fabricate drug interactions. Only explain what is explicitly
   provided in the input data. If no interaction text is provided,
   say so clearly.

2. Classify severity ONLY as one of these exact values:
   "low", "moderate", "high", "contraindicated", or "none"

3. Write all explanations in plain English that a 10th-grade student
   can understand. No medical jargon without immediate explanation.

4. For HIGH or CONTRAINDICATED severity, you MUST end plain_explanation
   with: "Please consult your doctor or pharmacist immediately before
   taking these medications together."

5. NEVER tell the user to stop taking a medication. Only recommend
   professional consultation.

6. NEVER diagnose any medical condition.

7. NEVER recommend specific dosages.

8. If interaction_text is empty or found is false, set:
   severity = "none"
   plain_explanation = "No known interaction detected in current
   databases. This does not guarantee safety — always consult
   your pharmacist before combining medications."

9. Suggest safer_alternatives ONLY when provided in input data.
   NEVER invent alternative drugs.

10. Keep plain_explanation between 50 and 130 words.

11. Keep what_to_watch_for to 1-2 sentences maximum.

12. Keep action_required to 1 sentence maximum.

13. Remain empathetic, calm, and non-alarmist in tone always.

14. Return ONLY valid JSON. No preamble, no markdown fences,
    no explanation outside the JSON structure.

15. The overall_severity must be the HIGHEST severity found
    across ALL pairs — not an average.

SEVERITY REFERENCE:
- contraindicated: Never take together. Life-threatening risk.
- high: Serious risk. Doctor consultation required immediately.
- moderate: Notable risk. Monitor closely. Discuss with doctor.
- low: Minor risk. Mention at next routine appointment.
- none: No known interaction in current databases."""


# ═══════════════════════════════════════════════════════════════════
#  EXPECTED OUTPUT FORMAT — Shown to Claude in every prompt
# ═══════════════════════════════════════════════════════════════════
EXPECTED_FORMAT = {
    "interactions": [
        {
            "drug1":             "string — first drug name",
            "drug2":             "string — second drug name",
            "severity":          "low|moderate|high|contraindicated|none",
            "severity_emoji":    "🚫|🔴|🟡|🟢|⚪",
            "plain_explanation": "string — 50 to 130 words, plain English",
            "what_to_watch_for": "string — 1-2 sentences max",
            "action_required":   "string — 1 sentence max",
            "safer_alternatives": ["string array — only if provided"],
        }
    ],
    "overall_severity": "low|moderate|high|contraindicated|none",
    "summary":          "string — 1-2 sentences, total interactions found",
    "disclaimer":       "string — standard medical disclaimer",
}


def build_analysis_prompt(
    pairs_data: List[Dict],
    patient_context: Optional[Dict] = None,
) -> str:
    """
    Build the user message to send to Claude.

    Args:
        pairs_data: List of raw interaction dicts from OpenFDA
        patient_context: Optional patient info (age, gender, etc.)

    Returns:
        Formatted JSON string for Claude user message
    """
    # Clean and validate pairs
    cleaned_pairs = []
    for pair in pairs_data:
        cleaned_pairs.append({
            "drug1":            pair.get("drug1", "Unknown"),
            "drug2":            pair.get("drug2", "Unknown"),
            "interaction_text": pair.get("interaction_text", ""),
            "found":            pair.get("found", False),
            "severity_hint":    pair.get("severity", "none"),
            "source":           pair.get("source", "OpenFDA"),
            "safer_alternatives": pair.get("safer_alternatives", []),
        })

    # Build context section
    context_note = ""
    if patient_context:
        parts = []
        if patient_context.get("age"):
            parts.append(f"Patient age: {patient_context['age']}")
        if patient_context.get("gender"):
            parts.append(f"Gender: {patient_context['gender']}")
        if patient_context.get("allergies"):
            parts.append(
                f"Known allergies: "
                f"{', '.join(patient_context['allergies'])}"
            )
        if patient_context.get("conditions"):
            parts.append(
                f"Medical conditions: "
                f"{', '.join(patient_context['conditions'])}"
            )
        if parts:
            context_note = (
                "PATIENT CONTEXT (use to personalise tone only, "
                "do NOT change severity classification):\n"
                + "\n".join(parts)
                + "\n\n"
            )

    prompt = f"""{context_note}Analyse these drug interactions and return
a JSON response matching EXACTLY this structure:

{json.dumps(EXPECTED_FORMAT, indent=2)}

DRUG INTERACTION DATA TO ANALYSE:
{json.dumps(cleaned_pairs, indent=2)}

IMPORTANT REMINDERS:
- overall_severity = highest severity across ALL pairs
- For pairs where found=false, severity must be "none"
- severity_hint is pre-calculated — use as a guide only
- Do NOT invent interaction data not present in interaction_text
- Return ONLY the JSON object, nothing else"""

    logger.debug(
        f"Prompt built: {len(cleaned_pairs)} pairs, "
        f"{len(prompt)} chars"
    )
    return prompt


def build_chat_prompt(
    user_message: str,
    history: List[Dict],
) -> List[Dict]:
    """
    Build messages array for Claude chat endpoint.

    Args:
        user_message: The user's question
        history: Previous conversation messages

    Returns:
        Messages array for Claude API
    """
    messages = []

    # Add conversation history (last 10 messages max)
    recent_history = history[-10:] if len(history) > 10 else history

    for msg in recent_history:
        role    = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ["user", "assistant"] and content:
            messages.append({
                "role":    role,
                "content": content,
            })

    # Add current message
    messages.append({
        "role":    "user",
        "content": user_message,
    })

    return messages


CHAT_SYSTEM_PROMPT = """You are RxChat, a helpful and friendly medical
information assistant for MedSafe AI. You answer questions about drug
safety, interactions, and medications.

RULES:
1. Always recommend consulting a doctor for personal medical decisions.
2. Never diagnose conditions or recommend specific dosages.
3. Keep answers concise — under 150 words.
4. If asked about a specific drug combination, clearly state the
   interaction risk level if you know it.
5. If unsure, say so honestly and recommend professional consultation.
6. Never tell users to stop taking prescribed medications.
7. Be warm, empathetic, and non-alarmist.
8. End responses about serious interactions with:
   "Please discuss this with your doctor or pharmacist."

You have access to general pharmacology knowledge. Always prioritise
patient safety above all else."""


def validate_claude_response(response_text: str) -> Dict:
    """
    Validate and parse Claude's JSON response.

    Args:
        response_text: Raw text from Claude API

    Returns:
        Parsed and validated response dict

    Raises:
        ValueError: If response cannot be parsed or is invalid
    """
    import json
    import re

    # Strip markdown fences if present
    cleaned = response_text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$',    '', cleaned)
    cleaned = cleaned.strip()

    # Parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(
            f"Claude JSON parse error: {e}\n"
            f"Response: {response_text[:200]}"
        )
        raise ValueError(f"Invalid JSON from Claude: {e}")

    # Validate required fields
    required = [
        "interactions",
        "overall_severity",
        "summary",
        "disclaimer",
    ]
    for field in required:
        if field not in data:
            raise ValueError(
                f"Missing required field '{field}' in Claude response"
            )

    # Validate interactions array
    if not isinstance(data["interactions"], list):
        raise ValueError("'interactions' must be a list")

    # Validate each interaction
    valid_severities = {
        "low", "moderate", "high", "contraindicated", "none"
    }
    for i, interaction in enumerate(data["interactions"]):
        if interaction.get("severity") not in valid_severities:
            logger.warning(
                f"Invalid severity in interaction {i}: "
                f"'{interaction.get('severity')}' — setting to 'none'"
            )
            interaction["severity"] = "none"

        # Ensure all required fields exist
        interaction.setdefault("severity_emoji",    "⚪")
        interaction.setdefault("plain_explanation", "")
        interaction.setdefault("what_to_watch_for", "")
        interaction.setdefault("action_required",   "")
        interaction.setdefault("safer_alternatives", [])

    # Validate overall severity
    if data["overall_severity"] not in valid_severities:
        data["overall_severity"] = "none"

    logger.info(
        f"Claude response validated: "
        f"{len(data['interactions'])} interactions, "
        f"overall={data['overall_severity']}"
    )

    return data


def build_fallback_response(
    pairs_data: List[Dict],
    disclaimer: str,
) -> Dict:
    """
    Build a safe fallback response when Claude API fails.
    Uses pre-classified severity from keyword engine.
    """
    from app.services.severity_classifier import (
        get_severity_emoji,
        get_overall_severity,
    )

    interactions = []
    severities   = []

    for pair in pairs_data:
        severity  = pair.get("severity", "none")
        severities.append(severity)
        emoji     = get_severity_emoji(severity)
        found     = pair.get("found", False)

        if found and severity != "none":
            explanation = (
                f"An interaction has been detected between "
                f"{pair['drug1']} and {pair['drug2']}. "
                f"Severity is classified as {severity}. "
                f"AI explanation is temporarily unavailable. "
                f"Please consult your pharmacist for details."
            )
        else:
            explanation = (
                f"No known interaction detected between "
                f"{pair['drug1']} and {pair['drug2']} in "
                f"current databases. Always consult your pharmacist."
            )

        interactions.append({
            "drug1":             pair.get("drug1", ""),
            "drug2":             pair.get("drug2", ""),
            "severity":          severity,
            "severity_emoji":    emoji,
            "plain_explanation": explanation,
            "what_to_watch_for": "",
            "action_required":   "Consult your pharmacist.",
            "safer_alternatives": pair.get("safer_alternatives", []),
        })

    overall = get_overall_severity(severities)

    return {
        "interactions":    interactions,
        "overall_severity": overall,
        "summary": (
            f"{len([i for i in interactions if i['severity'] != 'none'])} "
            f"interaction(s) detected. "
            f"AI explanation temporarily unavailable."
        ),
        "disclaimer": disclaimer,
        "fallback":   True,
    }