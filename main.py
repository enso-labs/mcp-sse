# mcp/main.py
import subprocess
import uvicorn
from mcp_wrap.server import FastMCP

from src.config import Config
from src.middleware.api_key import middleware

# Initialize FastMCP server instance
mcp = FastMCP(
    name=Config.APP_NAME.value,
    instructions=Config.APP_INSTRUCTIONS.value,
    settings={
        'debug': Config.APP_DEBUG.value,          # Enable debug mode
        'port': Config.APP_PORT.value,          # Port to run server on
        'log_level': Config.APP_LOG_LEVEL.value,  # Logging verbosity
    }
)

@mcp.tool()
def shell_command(command: str) -> str:
    """Execute a shell command"""
    ctx = mcp.get_context()
    middleware(ctx.request_context)
    return subprocess.check_output(command, shell=True).decode()

if __name__ == "__main__":
    print(f"Starting MCP server... {Config.APP_NAME.value} on port {Config.APP_PORT.value}")
    # Start server with Server-Sent Events transport
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=Config.APP_PORT.value, 
        log_level=Config.APP_LOG_LEVEL.value.lower(),
    )