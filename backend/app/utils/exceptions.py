# app/utils/exceptions.py
from fastapi import HTTPException


class MedSafeException(Exception):
    """Base exception for MedSafe AI."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DrugNotFoundException(MedSafeException):
    def __init__(self, drug_name: str):
        super().__init__(
            message=f"Drug '{drug_name}' could not be identified.",
            status_code=404
        )


class InsufficientDrugsException(MedSafeException):
    def __init__(self):
        super().__init__(
            message="Please enter at least 2 medications to check.",
            status_code=400
        )


class TooManyDrugsException(MedSafeException):
    def __init__(self, max_count: int):
        super().__init__(
            message=f"Maximum {max_count} medications allowed per check.",
            status_code=400
        )


class ExternalAPIException(MedSafeException):
    def __init__(self, api_name: str):
        super().__init__(
            message=f"{api_name} is temporarily unavailable. "
                    f"Please try again in a moment.",
            status_code=503
        )


class AIServiceException(MedSafeException):
    def __init__(self):
        super().__init__(
            message="AI explanation service is temporarily unavailable.",
            status_code=503
        )