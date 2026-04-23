# app/routers/history.py
import logging
from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional
from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/history")
async def get_history(
    request: Request,
    page:  int = Query(default=1,  ge=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    """
    Get paginated medication check history.
    For now returns session-based history.
    Full auth protected version comes in Week 4.
    """
    db = get_db()

    if db is None:
        return {
            "checks":  [],
            "total":   0,
            "page":    page,
            "limit":   limit,
            "message": "Database not available",
        }

    try:
        skip  = (page - 1) * limit
        total = await db.medication_checks.count_documents({})

        cursor = (
            db.medication_checks
            .find(
                {},
                {
                    "check_id":           1,
                    "drugs":              1,
                    "overall_severity":   1,
                    "interactions_found": 1,
                    "timestamp":          1,
                    "_id":                0,
                }
            )
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        checks = await cursor.to_list(length=limit)

        return {
            "checks": checks,
            "total":  total,
            "page":   page,
            "limit":  limit,
        }

    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return {
            "checks":  [],
            "total":   0,
            "page":    page,
            "limit":   limit,
        }


@router.delete("/history/{check_id}")
async def delete_history(
    check_id: str,
    request:  Request,
):
    """Delete a specific medication check."""
    db = get_db()

    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )

    try:
        # Delete check
        check_result = await db.medication_checks.delete_one(
            {"check_id": check_id}
        )

        # Delete associated results
        await db.interaction_results.delete_one(
            {"check_id": check_id}
        )

        if check_result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Check '{check_id}' not found."
            )

        return {"deleted": True, "check_id": check_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not delete history item."
        )