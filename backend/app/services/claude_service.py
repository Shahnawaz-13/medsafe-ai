# app/services/claude_service.py
import json
import logging
import time
from typing import List, Dict, Optional
from groq import Groq
from app.config import settings
from app.services.prompt_builder import (
    SYSTEM_PROMPT,
    CHAT_SYSTEM_PROMPT,
    build_analysis_prompt,
    build_chat_prompt,
    validate_claude_response,
    build_fallback_response,
)

logger = logging.getLogger(__name__)

# ── Groq Models ───────────────────────────────────────────────────────
GROQ_MODEL      = "llama-3.3-70b-versatile"  # Best quality (free)
GROQ_MODEL_FAST = "llama-3.1-8b-instant"     # Fastest (chat)


def _get_client() -> Groq:
    """Create and return Groq client."""
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not set in environment variables. "
            "Get free key at: https://console.groq.com"
        )
    return Groq(api_key=settings.groq_api_key)


async def get_interaction_explanations(
    pairs_data: List[Dict],
    patient_context: Optional[Dict] = None,
) -> Dict:
    """
    Send drug interaction data to Groq LLaMA and get
    plain-language AI explanations.

    Args:
        pairs_data: List of raw interaction dicts from OpenFDA
        patient_context: Optional patient info dict

    Returns:
        Validated AI response dict with explanations
    """
    if not pairs_data:
        logger.warning("No pairs data provided to AI")
        return build_fallback_response([], settings.disclaimer)

    t_start = time.time()

    try:
        client = _get_client()

        # Build prompt
        user_prompt = build_analysis_prompt(
            pairs_data, patient_context
        )

        logger.info(
            f"Calling Groq API: {len(pairs_data)} pairs, "
            f"model={GROQ_MODEL}"
        )

        # Call Groq API
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role":    "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role":    "user",
                    "content": user_prompt,
                },
            ],
            max_tokens=2000,
            temperature=0.1,    # Low for medical accuracy
        )

        # Extract response text
        response_text = response.choices[0].message.content
        t_elapsed     = round(time.time() - t_start, 2)

        logger.info(
            f"Groq response received: "
            f"time={t_elapsed}s, "
            f"input_tokens={response.usage.prompt_tokens}, "
            f"output_tokens={response.usage.completion_tokens}"
        )

        # Validate and parse JSON response
        validated = validate_claude_response(response_text)

        # Ensure disclaimer always present
        if not validated.get("disclaimer"):
            validated["disclaimer"] = settings.disclaimer

        # Add metadata
        validated["_meta"] = {
            "model":         GROQ_MODEL,
            "provider":      "groq",
            "response_time": t_elapsed,
            "input_tokens":  response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

        return validated

    except json.JSONDecodeError as e:
        logger.error(f"Groq JSON parse error: {e}")
        return _error_fallback(
            pairs_data,
            "AI returned invalid format. Using pre-classified data."
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"Groq API error: {error_msg}",
            exc_info=True
        )

        # Handle specific Groq errors
        if "rate_limit" in error_msg.lower():
            return _error_fallback(
                pairs_data,
                "AI rate limit reached. Please wait 1 minute."
            )
        if "authentication" in error_msg.lower():
            return _error_fallback(
                pairs_data,
                "AI service configuration error. Check GROQ_API_KEY."
            )
        if "model" in error_msg.lower():
            return _error_fallback(
                pairs_data,
                "AI model unavailable. Try again shortly."
            )

        return _error_fallback(
            pairs_data,
            "AI service temporarily unavailable."
        )


async def get_chat_response(
    message: str,
    history: List[Dict],
) -> str:
    """
    Get conversational response from Groq for RxChat.

    Args:
        message: User's question
        history: Previous conversation messages

    Returns:
        AI response as string
    """
    if not message.strip():
        return "Please ask a question about your medications."

    try:
        client = _get_client()

        # Build messages with history
        messages = [
            {
                "role":    "system",
                "content": CHAT_SYSTEM_PROMPT,
            }
        ]

        # Add recent history (last 8 messages)
        recent = history[-8:] if len(history) > 8 else history
        for msg in recent:
            role    = msg.get("role", "user")
            content = msg.get("content", "")
            if content and role in ["user", "assistant"]:
                messages.append({
                    "role":    role,
                    "content": content,
                })

        # Add current message
        messages.append({
            "role":    "user",
            "content": message,
        })

        # Use faster model for chat
        response = client.chat.completions.create(
            model=GROQ_MODEL_FAST,
            messages=messages,
            max_tokens=600,
            temperature=0.3,
        )

        reply = response.choices[0].message.content.strip()

        logger.info(
            f"RxChat response: "
            f"{len(reply)} chars, "
            f"tokens={response.usage.completion_tokens}"
        )

        return reply

    except Exception as e:
        logger.error(f"RxChat Groq error: {e}")
        return (
            "I am having trouble responding right now. "
            "Please consult your pharmacist directly "
            "for drug safety questions."
        )


async def test_claude_connection() -> Dict:
    """
    Test Groq API connectivity.
    Used by /health/claude endpoint.
    """
    try:
        client = _get_client()

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role":    "user",
                    "content": (
                        "Reply with exactly this text and nothing else: "
                        "MedSafe AI connected"
                    ),
                }
            ],
            max_tokens=20,
            temperature=0,
        )

        reply = response.choices[0].message.content.strip()

        return {
            "status":   "ok",
            "provider": "groq",
            "model":    GROQ_MODEL,
            "reply":    reply,
        }

    except Exception as e:
        return {
            "status":   "error",
            "provider": "groq",
            "model":    GROQ_MODEL,
            "error":    str(e),
        }


def _error_fallback(
    pairs_data: List[Dict],
    error_message: str,
) -> Dict:
    """Build safe fallback when Groq fails."""
    logger.warning(f"AI fallback active: {error_message}")
    fallback = build_fallback_response(
        pairs_data,
        settings.disclaimer
    )
    fallback["_error"] = error_message
    return fallback