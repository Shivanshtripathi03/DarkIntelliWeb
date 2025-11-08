import requests
import os

urls = [
    "https://httpbin.org/html",
    "https://example.com"
]

proxies = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050"
}

os.makedirs("data/html", exist_ok=True)

for i, url in enumerate(urls):
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            filename = f"data/html/page_{i}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved: {filename}")
        else:
            print(f"Failed to fetch {url}, status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

