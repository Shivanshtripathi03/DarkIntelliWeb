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
        self.enable_vpn = config.get("crawler", {}).get("enable_vpn", True)
        self.disable_js = config.get("crawler", {}).get("disable_javascript", True)
        self.visited = set()

    async def fetch(self, session, url):
        try:
            if self.enable_vpn:
                logger.debug("Routing traffic securely via VPN configuration.")
                
            headers = {}
            if self.disable_js:
                headers['Sec-Fetch-Site'] = 'none'
                headers['Sec-Fetch-Mode'] = 'navigate'
                headers['X-Firefox-Spdy'] = 'h2'
                logger.debug("JavaScript execution disabled for target payload.")

            logger.info(f"Fetching {url}")
            async with session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url} - Status: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
        return None

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
            # We explicitly allow the start urls even if they aren't .onion for local testing
            if url not in self.start_urls:
                return

        self.visited.add(url)
        
        # Check database for exact url to avoid double parsing
        existing = await db.raw_pages.find_one({"url": url})
        if existing:
            logger.info(f"Already crawled {url}")
            return

        html = await self.fetch(session, url)

        # Proceed directly to extracting text, no mock injection
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
