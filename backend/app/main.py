import os
import sys
import asyncio

# Resolve NotImplementedError on Windows by forcing ProactorEventLoopPolicy even if Uvicorn resets it
if sys.platform == 'win32':
    original_set_policy = asyncio.set_event_loop_policy
    def patched_set_policy(policy):
        # Force Proactor policy
        original_set_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.set_event_loop_policy = patched_set_policy
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from app.services.router import route_task, active_sessions
from app.models.session import AgentSession

app = FastAPI(title="EasyBrowse Web Automation Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure screenshots directory exists and is mounted
screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "screenshots"))
os.makedirs(screenshots_dir, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, payload: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(payload)
                except Exception:
                    pass

manager = ConnectionManager()

# Pydantic Schemas
class AgentRequest(BaseModel):
  goal: str
  url: Optional[str] = ""

class ResumeRequest(BaseModel):
    input: str

# Helper to send real-time updates via WebSockets
async def send_session_update(session: AgentSession, screenshot_url: Optional[str] = None):
    payload = {
        "session_id": session.session_id,
        "step": session.current_step,
        "status": session.status,
        "current_url": session.current_url,
        "current_action": session.current_action,
        "screenshot_url": screenshot_url,
        "validation_errors": session.validation_errors,
        "history": [
            {
                "step": h.get("step"),
                "tool": h.get("tool") or h.get("action"),
                "success": h.get("success"),
                "reasoning": h.get("reasoning", ""),
                "message": h.get("message") or h.get("result", "")
            } for h in session.history
        ]
    }
    await manager.broadcast(session.session_id, payload)

@app.post("/agent/run")
async def run_agent_endpoint(request: AgentRequest, background_tasks: BackgroundTasks):
    session_id = f"sess_{os.urandom(4).hex()}"
    
    async def task_runner():
        session = AgentSession(
            session_id=session_id,
            goal=request.goal
        )
        active_sessions[session_id] = session
        
        async def updater(s: AgentSession, scr_url: Optional[str] = None):
            await send_session_update(s, scr_url)
            
        await route_task(
            session_id=session_id,
            goal=request.goal,
            starting_url=request.url or "",
            send_update=updater
        )
        
    background_tasks.add_task(task_runner)
    return {"session_id": session_id}

@app.get("/agent/status/{session_id}")
async def get_agent_status(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = active_sessions[session_id]
    return {
        "status": session.status,
        "current_step": session.current_step,
        "current_url": session.current_url,
        "current_action": session.current_action,
        "history": session.history
    }

@app.post("/agent/stop/{session_id}")
async def stop_agent(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = active_sessions[session_id]
    session.status = "stopped"
    session.current_action = "Stopped by user intervention."
    return {"message": "Session stopped successfully."}

@app.post("/agent/resume/{session_id}")
async def resume_agent(session_id: str, request: ResumeRequest):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = active_sessions[session_id]
    session.user_input = request.input
    if session.resume_event:
        # Since uvicorn runs in a main loop, and route_task thread runs its own loop,
        # session.resume_event was created in the thread's loop.
        # We must trigger it thread-safely!
        loop = session.resume_event._loop
        loop.call_soon_threadsafe(session.resume_event.set)
    return {"message": "Session resumed."}

@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    # Send initial state if session already exists
    if session_id in active_sessions:
        session = active_sessions[session_id]
        await send_session_update(session)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
