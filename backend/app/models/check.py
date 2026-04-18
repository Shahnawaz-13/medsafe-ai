# app/models/check.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DrugEntry(BaseModel):
    input_name: str
    normalized_name: str
    rxcui: Optional[str] = None
    dosage: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class MedicationCheckModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    session_id: str
    drugs: List[DrugEntry]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "arbitrary_types_allowed": True,
    }