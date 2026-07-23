import asyncio
import os
from playwright.async_api import async_playwright
from config.logger import setup_logger

logger = setup_logger("browser_worker")

TOR_PROXY_URL = os.environ.get("TOR_PROXY_URL", "socks5://localhost:9050")


async def fetch_with_js(url: str, timeout_ms: int = 30000) -> str | None:
    """Fetch a page using a real browser (Firefox via Playwright) routed through Tor.
    
    Use this for JS-heavy .onion sites where plain HTTP fetch returns
    near-empty content. The browser executes JavaScript and returns the
    fully rendered DOM.
    """
    html = None
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(
                proxy={"server": TOR_PROXY_URL}
            )
            context = await browser.new_context(
                java_script_enabled=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"
            )
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=timeout_ms, wait_until="networkidle")
                html = await page.content()
                logger.info(f"Browser-rendered {url} ({len(html)} chars)")
            except Exception as e:
                logger.error(f"Browser navigation error for {url}: {e}")
            finally:
                await browser.close()
    except Exception as e:
        logger.error(f"Playwright launch error: {e}")
    return html


def fetch_with_js_sync(url: str, timeout_ms: int = 30000) -> str | None:
    """Synchronous wrapper for use from Celery tasks."""
    return asyncio.run(fetch_with_js(url, timeout_ms))
