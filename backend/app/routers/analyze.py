# app/routers/analyze.py
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from app.middleware.rate_limit import limiter
from app.config import settings
from app.models.interaction import AnalyzeRequest, AnalysisResult
from app.services.normaliser import normalize_drug_list
from app.services.pair_generator import generate_pairs
from app.services.interaction_resolver import resolve_all_pairs
from app.services.alternative_service import get_alternatives_for_pairs
from app.services.claude_service import get_interaction_explanations
from app.services.severity_classifier import (
    get_overall_severity,
    get_severity_emoji,
)
from app.services.cache_service import get_cache_stats
from app.database import get_db
from app.utils.helpers import (
    generate_session_id,
    sanitize_drug_name,
    format_timestamp,
)
from app.utils.exceptions import (
    InsufficientDrugsException,
    TooManyDrugsException,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-interaction")
@limiter.limit("30/minute")
async def analyze_interaction(
    request: Request,
    body: AnalyzeRequest,
):
    """
    Core drug interaction analysis endpoint.

    Full pipeline:
    1. Validate input
    2. Normalize drug names via RxNorm
    3. Generate all drug pairs
    4. Resolve interactions via OpenFDA (cache-first)
    5. Add safer alternatives
    6. Generate AI explanations via Groq
    7. Save check to MongoDB
    8. Return complete interaction report
    """
    start_time = datetime.utcnow()
    check_id   = str(uuid.uuid4())

    logger.info(
        f"Analyze request: "
        f"drugs={body.drugs}, "
        f"check_id={check_id}"
    )

    # ── Step 1: Validate input ────────────────────────────────────────
    # Clean drug names
    cleaned_drugs = [
        sanitize_drug_name(d)
        for d in body.drugs
        if d and d.strip()
    ]
    cleaned_drugs = [d for d in cleaned_drugs if len(d) >= 2]

    if len(cleaned_drugs) < 2:
        raise HTTPException(
            status_code=400,
            detail={
                "error":   "Insufficient medications",
                "message": "Please enter at least 2 medication names.",
                "code":    "MIN_DRUGS_REQUIRED",
            }
        )

    if len(cleaned_drugs) > settings.max_drugs_per_request:
        raise HTTPException(
            status_code=400,
            detail={
                "error":   "Too many medications",
                "message": (
                    f"Maximum {settings.max_drugs_per_request} "
                    f"medications allowed per check."
                ),
                "code":    "MAX_DRUGS_EXCEEDED",
            }
        )

    # ── Step 2: Normalize drug names ──────────────────────────────────
    logger.info(f"Normalising {len(cleaned_drugs)} drugs...")
    normalized = await normalize_drug_list(cleaned_drugs)

    # Log normalization results
    found_count = sum(1 for r in normalized if r["found"])
    logger.info(
        f"Normalization: {found_count}/{len(cleaned_drugs)} identified"
    )

    # Warn if too many drugs unrecognized
    if found_count == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error":   "Drugs not recognized",
                "message": (
                    "None of the entered medication names could be "
                    "identified. Please check spelling and try again."
                ),
                "code":    "DRUGS_NOT_FOUND",
            }
        )

    # ── Step 3: Generate drug pairs ───────────────────────────────────
    pairs = generate_pairs(normalized)

    if not pairs:
        raise HTTPException(
            status_code=400,
            detail={
                "error":   "Cannot generate pairs",
                "message": (
                    "Could not generate drug pairs. "
                    "Please check the medication names."
                ),
                "code":    "NO_PAIRS_GENERATED",
            }
        )

    logger.info(f"Generated {len(pairs)} pairs")

    # ── Step 4: Resolve interactions ──────────────────────────────────
    logger.info("Resolving interactions via OpenFDA...")
    raw_results = await resolve_all_pairs(pairs)

    cache_hits = sum(
        1 for r in raw_results if r.get("from_cache")
    )
    found_interactions = sum(
        1 for r in raw_results if r.get("found")
    )

    logger.info(
        f"Interactions: {found_interactions}/{len(pairs)} found, "
        f"{cache_hits} from cache"
    )

    # ── Step 5: Add safer alternatives ───────────────────────────────
    enriched = get_alternatives_for_pairs(raw_results)

    # ── Step 6: Generate AI explanations ─────────────────────────────
    logger.info("Generating AI explanations via Groq...")

    patient_context = None
    if body.age or body.gender or body.allergies:
        patient_context = {
            "age":      body.age,
            "gender":   body.gender,
            "allergies": body.allergies or [],
        }

    ai_result = await get_interaction_explanations(
        enriched,
        patient_context=patient_context,
    )

    # ── Step 7: Build final response ──────────────────────────────────
    interactions     = ai_result.get("interactions", [])
    overall_severity = ai_result.get(
        "overall_severity", "none"
    )

    # Ensure all interactions have required fields
    for interaction in interactions:
        interaction.setdefault("severity_emoji",
            get_severity_emoji(
                interaction.get("severity", "none")
            )
        )
        interaction.setdefault("safer_alternatives", [])
        interaction.setdefault("what_to_watch_for",  "")
        interaction.setdefault("action_required",     "")
        interaction.setdefault("mechanism",           "")
        interaction.setdefault("sources",             [])

    # Build normalized drug list for response
    drug_list = [
        {
            "input_name":      r["input_name"],
            "normalized_name": r["normalized_name"],
            "rxcui":           r.get("rxcui"),
            "identified":      r["found"],
        }
        for r in normalized
    ]

    # ── Step 8: Save to MongoDB ───────────────────────────────────────
    db = get_db()
    if db is not None:
        try:
            # Get user_id from request state if authenticated
            user_id = getattr(request.state, "user_id", None)

            check_doc = {
                "check_id":    check_id,
                "user_id":     user_id,
                "session_id":  body.session_id or generate_session_id(),
                "drugs":       drug_list,
                "pairs_count": len(pairs),
                "interactions_found": found_interactions,
                "overall_severity":   overall_severity,
                "timestamp":   datetime.utcnow(),
            }
            await db.medication_checks.insert_one(check_doc)

            # Save interaction results
            result_doc = {
                "check_id":    check_id,
                "interactions": interactions,
                "overall_severity": overall_severity,
                "summary":     ai_result.get("summary", ""),
                "created_at":  datetime.utcnow(),
            }
            await db.interaction_results.insert_one(result_doc)

            logger.info(f"Check saved to MongoDB: {check_id}")

        except Exception as e:
            logger.error(
                f"MongoDB save error (non-critical): {e}"
            )
            # Don't fail the request if save fails

    # ── Build final response ──────────────────────────────────────────
    elapsed_ms = int(
        (datetime.utcnow() - start_time).total_seconds() * 1000
    )

    response_data = {
        "check_id":          check_id,
        "drugs_submitted":   len(cleaned_drugs),
        "drugs_identified":  found_count,
        "drug_list":         drug_list,
        "pairs_checked":     len(pairs),
        "interactions_found": found_interactions,
        "pairs":             interactions,
        "overall_severity":  overall_severity,
        "overall_emoji":     get_severity_emoji(overall_severity),
        "summary":           ai_result.get("summary", ""),
        "disclaimer":        ai_result.get(
            "disclaimer", settings.disclaimer
        ),
        "generated_at":      format_timestamp(start_time),
        "response_time_ms":  elapsed_ms,
        "ai_provider":       "groq",
        "cached_pairs":      cache_hits,
        "is_fallback":       ai_result.get("fallback", False),
    }

    logger.info(
        f"Analysis complete: "
        f"check_id={check_id}, "
        f"severity={overall_severity}, "
        f"time={elapsed_ms}ms"
    )

    return response_data