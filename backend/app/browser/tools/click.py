from playwright.async_api import Page
from typing import Dict, Any

async def click(page: Page, selector: str) -> Dict[str, Any]:
    """
    Clicks the element identified by the selector.
    """
    try:
        # Wait for the selector to be attached to the DOM and visible
        element = page.locator(selector).first
        await element.wait_for(state="visible", timeout=5000)
        await element.click(timeout=5000)
        return {
            "success": True,
            "message": f"Successfully clicked element with selector '{selector}'",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to click element '{selector}': {str(e)}",
            "data": {}
        }
