"""
Step 12 — Rate Limiting
Uses SlowAPI (Starlette-compatible wrapper around limits library).
Limits:
  - Global:      60 requests/minute per IP
  - Login:        5 requests/minute per IP (brute-force protection)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create the limiter — uses the client's IP address as the key
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
