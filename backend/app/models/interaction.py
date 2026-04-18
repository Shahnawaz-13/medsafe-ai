# app/models/interaction.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class Severity(str, Enum):
    low             = "low"
    moderate        = "moderate"
    high            = "high"
    contraindicated = "contraindicated"
    none            = "none"


class InteractionPair(BaseModel):
    drug1: str
    drug2: str
    severity: Severity = Severity.none
    severity_emoji: str = "⚪"
    plain_explanation: str = ""
    what_to_watch_for: str = ""
    action_required: str = ""
    safer_alternatives: List[str] = []
    mechanism: str = ""
    sources: List[str] = []

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "use_enum_values": True,
    }


class AnalysisResult(BaseModel):
    check_id: str
    pairs: List[InteractionPair]
    overall_severity: Severity = Severity.none
    summary: str = ""
    disclaimer: str = ""
    generated_at: str = ""
    cached: bool = False

    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
    }


class AnalyzeRequest(BaseModel):
    drugs: List[str] = Field(
        min_length=2,
        max_length=15
    )
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    allergies: Optional[List[str]] = []
    session_id: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }