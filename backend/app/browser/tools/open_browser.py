import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Tuple

async def open_browser(headless: bool = None) -> Tuple[Browser, BrowserContext, Page]:
    """
    Launches a Chromium browser instance and returns the browser, context, and page objects.
    """
    if headless is None:
        headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(
        headless=headless,
        args=["--disable-web-security", "--no-sandbox"]
    )
    # Set viewport size to standard desktop size for consistency
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    
    # Store reference to playwright_instance in browser object to prevent garbage collection and allow closing
    browser._playwright_instance = playwright_instance
    
    return browser, context, page
