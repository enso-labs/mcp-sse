from __future__ import annotations as _annotations

from typing import Any

from mcp.server import FastMCP as _FastMCP
from mcp.server.fastmcp.prompts import PromptManager
from mcp.server.fastmcp.resources import ResourceManager
from mcp.server.fastmcp.server import Settings, lifespan_wrapper
from mcp.server.fastmcp.tools import ToolManager
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from mcp.server.lowlevel.server import lifespan as default_lifespan
from mcp.server.sse import SseServerTransport

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from low_level import McpServer

logger = get_logger(__name__)


class FastMCP(_FastMCP):

    def __init__(
        self, name: str | None = None, instructions: str | None = None, **settings: Any
    ):
        self.settings = Settings(**settings)

        self._mcp_server = McpServer(
            name=name or "FastMCP",
            instructions=instructions,
            lifespan=lifespan_wrapper(self, self.settings.lifespan) if self.settings.lifespan else default_lifespan,
        )
        self._tool_manager = ToolManager(
            warn_on_duplicate_tools=self.settings.warn_on_duplicate_tools
        )
        self._resource_manager = ResourceManager(
            warn_on_duplicate_resources=self.settings.warn_on_duplicate_resources
        )
        self._prompt_manager = PromptManager(
            warn_on_duplicate_prompts=self.settings.warn_on_duplicate_prompts
        )
        self.dependencies = self.settings.dependencies

        # Set up MCP protocol handlers
        self._setup_handlers()

        # Configure logging
        configure_logging(self.settings.log_level)

    @property
    def mcp_server(self) -> McpServer:
        return self._mcp_server

    def sse_app(self) -> Starlette:
        """Return an instance of the SSE server app."""
        sse = SseServerTransport("/messages/")

        async def handle_sse(request: Request) -> None:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # type: ignore[reportPrivateUsage]
            ) as streams:
                await self.mcp_server.run(
                    streams[0],
                    streams[1],
                    self._mcp_server.create_initialization_options(),
                    scope=request.scope
                )

        return Starlette(
            debug=self.settings.debug,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )
