# app/config.py
from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    # AI
    claude_api_key: str = ""

    # Medical APIs
    openfda_api_key: str = ""
    rxnorm_base_url: str = "https://rxnav.nlm.nih.gov/REST"

    # Database
    mongodb_uri: str = ""
    mongodb_db_name: str = "medsafe"

    # Auth
    clerk_jwt_issuer: str = ""

    # App
    allowed_origins: List[str] = ["http://localhost:3000"]
    environment: str = "development"
    log_level: str = "INFO"
    max_drugs_per_request: int = 15
    cache_ttl_days: int = 7
    rate_limit_per_minute: int = 30

    # Disclaimer
    disclaimer: str = (
        "MedSafe AI provides general drug interaction information "
        "for educational purposes only. This tool does not constitute "
        "medical advice and is not a substitute for professional "
        "consultation. Always consult a licensed physician or "
        "pharmacist before making any medication decisions. "
        "In case of emergency, call your local emergency services."
    )

    # ── This validator handles BOTH formats ──────────────────────────
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string
            # e.g. "http://localhost:3000,https://app.vercel.app"
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()