# mcp/main.py
from contextlib import asynccontextmanager
import os
import subprocess
from starlette.exceptions import HTTPException
from dotenv import load_dotenv
import uvicorn

from server import FastMCP

# Load environment variables from .env file
load_dotenv()

# MCP API key
APP_NAME = os.getenv("APP_NAME", 'Terminal')
APP_DEBUG = os.getenv("APP_DEBUG", True)
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", 'DEBUG')
APP_PORT = os.getenv("APP_PORT", 8005)
MCP_API_KEY = os.getenv("MCP_API_KEY", 'test1234sfafd')

# Middleware function to check API key authentication
def middleware(headers):
    # Verify the x-api-key header matches the environment variable
    if headers.get("x-api-key") != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Server configuration settings
settings = {
    'debug': APP_DEBUG,          # Enable debug mode
    'port': APP_PORT,          # Port to run server on
    'log_level': APP_LOG_LEVEL,  # Logging verbosity
}

# Initialize FastMCP server instance
mcp = FastMCP(name=APP_NAME, **settings)

@mcp.tool()
def shell_command(command: str) -> str:
    """Execute a shell command"""
    ctx = mcp.get_context()
    request_context = ctx.request_context
    scope= request_context.scope
    headers = {k: v for k, v in scope.get("headers", {})} if scope is not None else {}
    middleware(headers)
    return subprocess.check_output(command, shell=True).decode()

if __name__ == "__main__":
    print(f"Starting MCP server... {APP_NAME} on port {APP_PORT}")
    # Start server with Server-Sent Events transport
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=APP_PORT, 
        log_level=APP_LOG_LEVEL.lower(),
    )