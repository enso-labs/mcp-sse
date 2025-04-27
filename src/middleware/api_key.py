from starlette.exceptions import HTTPException
from src.config import Config


def get_headers(req_ctx):
    scope = req_ctx.scope
    # Convert bytes headers to string dictionary
    headers = {
        k.decode('utf-8').lower(): v.decode('utf-8')
        for k, v in scope.get("headers", [])
    } if scope is not None else {}
    return headers

# Middleware function to check API key authentication
def middleware(req_ctx):
    scope = req_ctx.scope
    # Convert bytes headers to string dictionary
    headers = {
        k.decode('utf-8').lower(): v.decode('utf-8')
        for k, v in scope.get("headers", [])
    } if scope is not None else {}

    if headers.get("x-mcp-key") != Config.MCP_API_KEY.value:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True