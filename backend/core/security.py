from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from core.config import settings

api_key_header = APIKeyHeader(name='X-API-KEY', auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key from request header.

    ---

    :param api_key: API key from request header.
    :type api_key: str

    :raises HTTPException: If API key is invalid.
    """
    if api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado: Token inválido.")
    
    return api_key
