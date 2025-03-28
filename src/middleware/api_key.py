from starlette.exceptions import HTTPException
from src.config import Config

# Middleware function to check API key authentication
def middleware(req_ctx):
    scope = req_ctx.scope
    headers = {k: v for k, v in scope.get("headers", {})} if scope is not None else {}

    if headers.get("x-api-key") != Config.MCP_API_KEY.value:
        raise HTTPException(status_code=401, detail="Unauthorized")