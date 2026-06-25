import threading
import asyncio
import uuid
import logging
import sys
from app.models.session import AgentSession
from app.browser.tools.open_browser import open_browser
from app.browser.tools.close_browser import close_browser
from app.agent.service import run_agent

logger = logging.getLogger(__name__)

# Keep a global dictionary of active sessions
active_sessions = {}

async def route_task(
    session_id: str,
    goal: str = "",
    starting_url: str = "",
    max_steps: int = 20,
    send_update = None
) -> str:
    """
    Spawns a dedicated thread with a ProactorEventLoop to run the browser automation,
    bypassing whatever event loop Uvicorn initialized on the main thread.
    """
    main_loop = asyncio.get_running_loop()
    
    # Thread-safe wrapper to execute updates on the main thread's event loop
    async def thread_safe_update(session: AgentSession, screenshot_url = None):
        if send_update:
            future = asyncio.run_coroutine_threadsafe(
                send_update(session, screenshot_url),
                main_loop
            )
            # Await the completion of the future in the child loop context
            await asyncio.wrap_future(future)

    result_container = []
    error_container = []

    def thread_target():
        try:
            # Force Windows Proactor loop inside the child thread
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Execute the internal runner inside the thread's new loop
            res = loop.run_until_complete(
                _route_task_internal(
                    session_id=session_id,
                    goal=goal,
                    starting_url=starting_url,
                    max_steps=max_steps,
                    send_update=thread_safe_update
                )
            )
            result_container.append(res)
        except Exception as e:
            logger.exception("Error inside routing thread:")
            error_container.append(e)
        finally:
            loop.close()

    # Start the worker thread
    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()
    
    # Wait for the thread to finish execution while keeping the main loop active
    while thread.is_alive():
        await asyncio.sleep(0.2)
        
    if error_container:
        return f"Error: {str(error_container[0])}"
        
    return result_container[0] if result_container else "Completed"


async def _route_task_internal(
    session_id: str,
    goal: str = "",
    starting_url: str = "",
    max_steps: int = 20,
    send_update = None
) -> str:
    """
    Internal execution path that runs inside the child thread's loop.
    """
    # Initialize the session state
    session = AgentSession(
        session_id=session_id,
        goal=goal,
        history=[{"max_steps": max_steps}]
    )
    
    active_sessions[session_id] = session
    
    try:
        # Launch browser context
        import os
        headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        browser, context, page = await open_browser(headless=headless)
        session.browser = browser
        session.context = context
        session.page = page
        session.current_url = "about:blank"
        
        if starting_url:
            session.current_action = f"Initializing starting page: {starting_url}..."
            if send_update:
                await send_update(session)
            from app.browser.tools.navigate import navigate
            await navigate(page, starting_url)
            session.current_url = page.url
            
        result = await run_agent(
            session=session,
            send_update=send_update
        )
            
        return result
        
    except Exception as e:
        logger.exception("Exception in router task runner:")
        session.status = "error"
        session.current_action = f"Fatal Error: {str(e)}"
        if send_update:
            await send_update(session)
        return f"Fatal Error: {str(e)}"
        
    finally:
        # Clean up browser objects
        if session.browser:
            await close_browser(session.browser, session.context, session.page)
            session.browser = None
            session.context = None
            session.page = None
        
        # Keep session info in memory, but clear large handles
        if session_id in active_sessions:
            logger.info(f"Session {session_id} finished execution.")

