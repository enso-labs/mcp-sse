# mcp/main.py
import uvicorn
from typing import Literal
from datetime import datetime
from mcp_wrap.server import FastMCP

from src.config import Config
from src.middleware.api_key import middleware
from src.utils.scrape import retrieve_webpage
from src.utils.shell import tool_shell_command
from src.utils.search import Search
from homeharvest import scrape_property

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
def web_scrape(url: str) -> str:
    """Scrape a web page"""
    return retrieve_webpage(url)

@mcp.tool()
def search_properties(
    location: str,
    past_days: int = 30,
    radius: float = 20,
    limit: int = 10,
    mls_only: bool = True,
    foreclosure: bool = False,
    extra_property_data: bool = True,
    exclude_pending: bool = True,
    property_type: Literal["single_family", "multi_family"] = ["single_family", "multi_family"],
    listing_type: Literal["sold", "for_sale", "for_rent", "pending"] = "for_sale",
) -> str:
    """Search for properties on homeharvest"""
    try:
        properties = scrape_property(
            location=location,
            past_days=past_days,
            radius=radius,
            limit=limit,
            mls_only=mls_only,
            foreclosure=foreclosure,
            extra_property_data=extra_property_data,
            exclude_pending=exclude_pending,
            property_type=property_type,
            listing_type=listing_type,
        ).to_json(orient='records')
        return properties
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(f"Starting MCP server... {Config.APP_NAME.value} on port {Config.APP_PORT.value}")
    # Start server with Server-Sent Events transport
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=Config.APP_PORT.value, 
        log_level=Config.APP_LOG_LEVEL.value.lower(),
    )