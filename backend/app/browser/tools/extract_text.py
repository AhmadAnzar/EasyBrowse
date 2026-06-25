from playwright.async_api import Page
from typing import Dict, Any

async def extract_text(page: Page, selector: str = "body") -> Dict[str, Any]:
    """
    Extracts visible text content from a given selector (defaults to "body").
    """
    try:
        element = page.locator(selector).first
        # Wait for presence
        await element.wait_for(state="attached", timeout=5000)
        text = await element.inner_text(timeout=5000)
        # Clean text spacing
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        clean_text = "\n".join(lines)
        return {
            "success": True,
            "message": f"Successfully extracted text from '{selector}'",
            "data": {
                "text": clean_text
            }
        }
    except Exception as e:
        # Fallback to general page text if custom selector fails
        if selector != "body":
            try:
                body_text = await page.locator("body").inner_text(timeout=3000)
                lines = [line.strip() for line in body_text.split("\n") if line.strip()]
                clean_text = "\n".join(lines)
                return {
                    "success": True,
                    "message": f"Custom selector '{selector}' failed ({str(e)}), fell back to body text",
                    "data": {
                        "text": clean_text
                    }
                }
            except Exception as body_err:
                return {
                    "success": False,
                    "message": f"Failed to extract text: {str(body_err)}",
                    "data": {}
                }
        return {
            "success": False,
            "message": f"Failed to extract text: {str(e)}",
            "data": {}
        }
