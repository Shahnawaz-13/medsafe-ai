# app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance — used across all routes
limiter = Limiter(key_func=get_remote_address)