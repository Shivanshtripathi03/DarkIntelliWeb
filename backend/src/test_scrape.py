import requests
import justext

proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

url = "https://httpbin.org/html"  # safe test page

print("Fetching:", url)
r = requests.get(url, proxies=proxies, timeout=30)
print("HTTP status:", r.status_code)
paras = justext.justext(r.text, justext.get_stoplist("English"))
clean = "\n\n".join([p.text for p in paras if not p.is_boilerplate])
print("\n--- Extracted text (first 800 chars) ---\n")
print(clean[:800])
