from playwright.async_api import Page
from typing import Dict, Any

async def navigate(page: Page, url: str) -> Dict[str, Any]:
    """
    Directs the browser to a specific URL and waits for the page load.
    """
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        
        response = await page.goto(url, wait_until="load", timeout=30000)
        return {
            "success": True,
            "message": f"Successfully navigated to {url}",
            "data": {
                "url": page.url,
                "status": response.status if response else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to navigate to {url}: {str(e)}",
            "data": {}
        }
