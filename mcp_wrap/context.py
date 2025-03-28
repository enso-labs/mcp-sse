from dataclasses import dataclass
from typing import Optional

from mcp.shared.context import RequestContext as _RequestContext, SessionT, LifespanContextT
from starlette.types import Scope

@dataclass
class RequestContext(_RequestContext[SessionT, LifespanContextT]):
    scope: Optional[Scope] = None