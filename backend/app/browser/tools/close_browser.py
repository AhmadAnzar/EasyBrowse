from playwright.async_api import Browser, BrowserContext, Page
import logging

logger = logging.getLogger(__name__)

async def close_browser(browser: Browser, context: BrowserContext = None, page: Page = None):
    """
    Closes the page, context, and browser instance, cleaning up playwright processes.
    """
    try:
        if page:
            await page.close()
    except Exception as e:
        logger.warning(f"Error closing page: {e}")
        
    try:
        if context:
            await context.close()
    except Exception as e:
        logger.warning(f"Error closing context: {e}")
        
    try:
        if browser:
            await browser.close()
            # Stop the playwright instance stored on the browser
            if hasattr(browser, "_playwright_instance"):
                await browser._playwright_instance.stop()
    except Exception as e:
        logger.warning(f"Error closing browser: {e}")
