from dataclasses import dataclass, field
from playwright.async_api import Page, BrowserContext, Browser
from typing import List, Dict, Any, Optional

@dataclass
class AgentSession:
    session_id: str
    goal: str
    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "init"
    current_step: int = 0
    current_url: str = ""
    current_action: str = ""
    start_time: float = 0.0
    resume_event: Any = None
    user_input: str = ""
    validation_errors: Optional[List[str]] = None
