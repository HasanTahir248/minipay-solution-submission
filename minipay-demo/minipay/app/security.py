from fastapi import Header, HTTPException

from app.config import settings


def require_api_key(x_api_key: str = Header(None)):
    """Simple shared-secret auth for the JSON API (satisfies requirements/05
    'authentication or access-control behavior'). Swap for OAuth2/JWT in a
    real deployment -- this is intentionally minimal for a demo."""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
