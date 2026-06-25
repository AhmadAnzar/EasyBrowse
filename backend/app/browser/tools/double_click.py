# pyrefly: ignore [missing-import]
from playwright.async_api import Page
from typing import Dict, Any, Optional

async def double_click(page: Page, selector: Optional[str] = None, x: Optional[float] = None, y: Optional[float] = None) -> Dict[str, Any]:
    """
    Performs a double-click on an element (via selector) or at specific coordinates.
    """
    try:
        if x is not None and y is not None:
            await page.mouse.click(x, y, click_count=2)
            return {
                "success": True,
                "message": f"Successfully double-clicked at coordinates ({x}, {y})",
                "data": {}
            }
        elif selector:
            element = page.locator(selector).first
            await element.wait_for(state="visible", timeout=5000)
            await element.dblclick(timeout=5000)
            return {
                "success": True,
                "message": f"Successfully double-clicked element with selector '{selector}'",
                "data": {}
            }
        else:
            return {
                "success": False,
                "message": "Neither selector nor coordinates provided for double-click.",
                "data": {}
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to double-click: {str(e)}",
            "data": {}
        }
