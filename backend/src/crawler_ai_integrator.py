#!/usr/bin/env python3
"""
Crawler + AI integrator
Saves results to darkintelliweb.db
Requirements (install in venv): pip install openai requests bs4
Run: export OPENAI_API_KEY="sk-..."  (or set in your env), then:
python crawler_ai_integrator.py
"""
import os
import time
import sqlite3
from typing import Optional

import requests
from bs4 import BeautifulSoup
import openai

# Use Tor SOCKS proxy
PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Read OpenAI key from environment
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_KEY:
    raise SystemExit("Set OPENAI_API_KEY in environment before running (export OPENAI_API_KEY='sk-...')")

openai.api_key = OPENAI_KEY

# Database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'darkintelliweb.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    content TEXT,
    ai_summary TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Replace these with the URLs (including .onion if you have them).
# IMPORTANT: only crawl sites you are allowed to crawl.
ONION_SITES = [
    # Example placeholders — replace with real targets you want to analyze
    # 'http://exampleonion1.onion',
    # 'http://exampleonion2.onion',
    'https://check.torproject.org/'  # non-onion test (works over Tor)
]

REQUEST_TIMEOUT = 20  # seconds


def fetch_content(url: str) -> Optional[str]:
    try:
        print(f"[fetch] {url}")
        r = requests.get(url, proxies=PROXIES, timeout=REQUEST_TIMEOUT, headers={'User-Agent': 'DarkIntelliWeb/1.0'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"[error] fetch_content({url}) -> {e}")
        return None


def analyze_with_ai(text: str) -> str:
    try:
        # Shorten text if extremely long
        prompt_text = text if len(text) < 15000 else text[:15000] + "\n\n[TRUNCATED]"
        system_msg = "You are a cybersecurity analyst assistant. Summarize potential threats, indicators of compromise, suspicious links, references to malware or illicit activity. Keep the summary concise (max 300 words)."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Analyze the following scraped content for potential cyber threats or security-relevant indicators:\n\n{prompt_text}"}
            ],
            max_tokens=400,
            temperature=0.0
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        print(f"[error] analyze_with_ai -> {e}")
        return "AI analysis failed: " + str(e)


def save_scan(url: str, content: str, ai_summary: str):
    c.execute("INSERT INTO scans (url, content, ai_summary) VALUES (?, ?, ?)", (url, content, ai_summary))
    conn.commit()
    print(f"[saved] {url}")


def main():
    if not ONION_SITES:
        print("No sites configured in ONION_SITES. Edit crawler_ai_integrator.py and add targets.")
        return

    for url in ONION_SITES:
        content = fetch_content(url)
        if not content:
            print(f"[skip] no content for {url}")
            time.sleep(3)
            continue
        ai_summary = analyze_with_ai(content)
        save_scan(url, content, ai_summary)
        # polite pause between requests
        time.sleep(5)

    print("All done. DB path:", DB_PATH)


if __name__ == '__main__':
    main()
