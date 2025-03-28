# mcp/main.py
from typing import Literal
import uvicorn
from mcp_wrap.server import FastMCP

from src.config import Config
from src.middleware.api_key import middleware
from src.utils.scrape import retrieve_webpage
from src.utils.shell import tool_shell_command
from src.utils.search import Search
# Initialize FastMCP server instance
mcp = FastMCP(
    name=Config.APP_NAME.value,
    instructions=Config.MCP_INSTRUCTIONS.value,
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
    return tool_shell_command(command)

@mcp.tool()
def web_scrape(url: str) -> str:
    """Scrape a web page"""
    return retrieve_webpage(url)

@mcp.tool()
def web_search(query: str, search_type: Literal["question", "context", None] = None) -> str:
    """Search the web
    
    Args:
        query: The search query
        search_type: Type of search to perform - "question" for question answering,
                     "context" for context search, or None for standard search
    """
    result = Search().query(query, search_type)
    return result

if __name__ == "__main__":
    print(f"Starting MCP server... {Config.APP_NAME.value} on port {Config.APP_PORT.value}")
    # Start server with Server-Sent Events transport
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=Config.APP_PORT.value, 
        log_level=Config.APP_LOG_LEVEL.value.lower(),
    )