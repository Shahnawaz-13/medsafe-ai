# app/routers/chat.py
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.middleware.rate_limit import limiter
from app.services.claude_service import get_chat_response
from app.utils.helpers import sanitize_drug_name

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role:    str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500
    )
    history: List[ChatMessage] = Field(
        default=[],
        max_length=20
    )

    model_config = {
        "str_strip_whitespace": True,
    }


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    body: ChatRequest,
):
    """
    Conversational AI endpoint for RxChat.
    Rate limited strictly — 10/min to control AI costs.
    """
    # Sanitize message
    message = body.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # Convert history to dict format
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in body.history
        if msg.content.strip()
    ]

    logger.info(
        f"RxChat: message_len={len(message)}, "
        f"history={len(history)}"
    )

    # Get AI response
    reply = await get_chat_response(message, history)

    return {
        "reply":     reply,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "provider":  "groq",
    }