from playwright.async_api import Page
from typing import Dict, Any

async def type_text(page: Page, selector: str, text: str) -> Dict[str, Any]:
    """
    Fills/types text into the element identified by the selector.
    """
    try:
        # Wait for the selector to be visible
        element = page.locator(selector).first
        await element.wait_for(state="visible", timeout=5000)
        
        # Focus the element
        await element.focus()
        # Clear existing text first
        await element.fill("")
        # Type text
        await element.type(text, delay=50, timeout=5000)
        
        # Dispatch events to trigger validation
        await element.dispatch_event("input")
        await element.dispatch_event("change")
        # Trigger blur to run validation handlers (like react-hook-form)
        await element.blur()
        
        return {
            "success": True,
            "message": f"Successfully typed text into element '{selector}'",
            "data": {}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to type text into element '{selector}': {str(e)}",
            "data": {}
        }
