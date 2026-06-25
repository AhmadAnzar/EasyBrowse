# pyrefly: ignore [missing-import]
from playwright.async_api import Page
from typing import Dict, Any

async def click_on_screen(page: Page, x: float, y: float) -> Dict[str, Any]:
    """
    Clicks the screen at coordinates x, y.
    """
    try:
        await page.mouse.click(x, y)
        return {
            "success": True,
            "message": f"Successfully clicked screen at coordinates ({x}, {y})",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to click screen at ({x}, {y}): {str(e)}",
            "data": {}
        }
