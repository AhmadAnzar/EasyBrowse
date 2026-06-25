from playwright.async_api import Page
from typing import Dict, Any

async def scroll(page: Page, direction: str = "down") -> Dict[str, Any]:
    """
    Scrolls the page up or down by one viewport height.
    """
    try:
        if direction.lower() == "down":
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.7)")
        elif direction.lower() == "up":
            await page.evaluate("window.scrollBy(0, -window.innerHeight * 0.7)")
        else:
            return {
                "success": False,
                "message": f"Invalid scroll direction: {direction}. Use 'up' or 'down'.",
                "data": {}
            }
        return {
            "success": True,
            "message": f"Successfully scrolled page {direction}",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to scroll: {str(e)}",
            "data": {}
        }
