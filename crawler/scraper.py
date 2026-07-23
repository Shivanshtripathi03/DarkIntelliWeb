import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

from config.loader import load_config
from config.logger import setup_logger
from database.db import db

logger = setup_logger("crawler")
config = load_config()


class DarkWebCrawler:
    def __init__(self, start_urls: list, proxy_url: str = None):
        self.start_urls = start_urls
        self.proxy_url = proxy_url or config.get("crawler", {}).get("proxy", "socks5://localhost:9050")
        self.max_depth = config.get("crawler", {}).get("max_depth", 2)
        self.timeout = config.get("crawler", {}).get("timeout_seconds", 60)
        self.circuit_rotation_interval = config.get("crawler", {}).get("circuit_rotation_interval", 10)
        self.js_content_threshold = config.get("crawler", {}).get("js_content_threshold", 200)
        self.visited = set()
        self._request_count = 0

    async def _maybe_rotate_circuit(self):
        """Rotate Tor circuit every N requests for anonymity."""
        self._request_count += 1
        if self._request_count % self.circuit_rotation_interval == 0:
            try:
                from crawler.tor_control import rotate_circuit
                await asyncio.to_thread(rotate_circuit)
                # Wait for the new circuit to be established
                await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"Circuit rotation skipped: {e}")

    async def fetch(self, session, url):
        try:
            await self._maybe_rotate_circuit()

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            logger.info(f"Fetching {url}")
            async with session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url} - Status: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
        return None

    async def _fetch_with_js_fallback(self, url: str, html: str | None) -> str | None:
        """If plain fetch returned minimal content, try JS rendering."""
        if html is None:
            return None

        text_length = len(BeautifulSoup(html, "html.parser").get_text(strip=True))
        if text_length < self.js_content_threshold:
            logger.info(f"Content too thin ({text_length} chars), attempting JS render for {url}")
            try:
                from crawler.browser_worker import fetch_with_js
                js_html = await fetch_with_js(url)
                if js_html:
                    js_text_length = len(BeautifulSoup(js_html, "html.parser").get_text(strip=True))
                    if js_text_length > text_length:
                        logger.info(f"JS render yielded {js_text_length} chars (up from {text_length})")
                        return js_html
            except ImportError:
                logger.debug("Playwright not available, skipping JS fallback.")
            except Exception as e:
                logger.warning(f"JS fallback failed for {url}: {e}")
        return html

    def clean_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        return text

    async def crawl_page(self, session, url, depth):
        if depth > self.max_depth or url in self.visited:
            return
        
        # Domain check: only crawl .onion, or exact original target
        parsed_url = urlparse(url)
        if not parsed_url.netloc.endswith('.onion') and '.onion' not in url:
            if url not in self.start_urls:
                return

        self.visited.add(url)
        
        # Check database for exact url to avoid double parsing
        existing = await db.raw_pages.find_one({"url": url})
        if existing:
            logger.info(f"Already crawled {url}")
            return

        html = await self.fetch(session, url)

        # Try JS-rendered fallback if content is thin
        html = await self._fetch_with_js_fallback(url, html)

        if html:
            text = self.clean_html(html)
            
            # Store in DB
            page_data = {
                "url": url,
                "html": html,
                "text": text,
                "timestamp": datetime.utcnow(),
                "processed": False
            }
            await db.raw_pages.insert_one(page_data)
            logger.info(f"Saved {url} to database")

            if depth < self.max_depth:
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    
                    parsed = urlparse(next_url)
                    if not parsed.scheme or parsed.scheme not in ['http', 'https']:
                        continue
                        
                    if parsed.netloc == parsed_url.netloc:
                        await self.crawl_page(session, next_url, depth + 1)

    async def run(self):
        connector = ProxyConnector.from_url(self.proxy_url) if self.proxy_url else None
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for url in self.start_urls:
                    if not url.startswith('http'):
                        url = 'http://' + url
                    tasks.append(self.crawl_page(session, url, 0))
                
                await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Crawler session error: {str(e)}")

if __name__ == "__main__":
    from config.loader import load_targets
    targets = load_targets()
    if targets:
        crawler = DarkWebCrawler(targets)
        asyncio.run(crawler.run())
    else:
        logger.warning("No targets found to crawl.")
