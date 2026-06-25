import os
import uuid
from playwright.async_api import Page
from typing import Dict, Any

async def screenshot(page: Page, session_id: str, step: int) -> Dict[str, Any]:
    """
    Captures a screenshot of the current page viewport and saves it.
    """
    try:
        # Determine path (save under a workspace relative path for backend/screenshots)
        screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "screenshots"))
        os.makedirs(screenshots_dir, exist_ok=True)
        
        filename = f"{session_id}_step_{step}.jpg"
        filepath = os.path.join(screenshots_dir, filename)
        
        await page.screenshot(path=filepath, type="jpeg", quality=70)
        
        # We return the URL path that the frontend will request (served statically)
        return {
            "success": True,
            "message": f"Screenshot saved for step {step}",
            "data": {
                "filename": filename,
                "screenshot_url": f"/screenshots/{filename}"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to capture screenshot: {str(e)}",
            "data": {}
        }
