import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv(override=True)

from app.models.session import AgentSession
from app.browser.tools.open_browser import open_browser
from app.browser.tools.close_browser import close_browser
from app.browser.tools.navigate import navigate
from app.agent.service import run_agent

async def run_cli_agent(goal: str, starting_url: str):
    session_id = f"sess_cli_{os.urandom(4).hex()}"
    print(f"=== Starting EasyBrowse CLI Agent Session: {session_id} ===")
    print(f"Goal: {goal}")
    if starting_url:
        print(f"Starting URL: {starting_url}")
    print("=========================================\n")

    # Set up session state
    session = AgentSession(
        session_id=session_id,
        goal=goal,
        history=[{"max_steps": 20}]
    )

    async def print_update(s: AgentSession, screenshot_url=None):
        step_info = f"[Step {s.current_step}] status={s.status}"
        action_info = f"Action: {s.current_action}"
        print(f"{step_info} | {action_info}")
        if screenshot_url:
            print(f"Screenshot taken: {screenshot_url}")

    # Launch browser context
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    print("Launching browser...")
    browser, context, page = await open_browser(headless=headless)
    session.browser = browser
    session.context = context
    session.page = page
    session.current_url = "about:blank"

    try:
        if starting_url:
            print(f"Navigating to starting URL: {starting_url}...")
            await navigate(page, starting_url)
            session.current_url = page.url

        result = await run_agent(session=session, send_update=print_update)
        print("\n=========================================")
        print("🎉 MISSION COMPLETED 🎉")
        print(f"Final AI Output Result:\n{result}")
        print("=========================================")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
    finally:
        if session.browser:
            await close_browser(session.browser, session.context, session.page)
            print("Browser closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EasyBrowse Web Automation Agent CLI")
    parser.add_argument("--goal", required=True, type=str, help="Goal or objective for the agent")
    parser.add_argument("--url", type=str, default="", help="Starting URL (optional)")
    args = parser.parse_args()

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(run_cli_agent(args.goal, args.url))
