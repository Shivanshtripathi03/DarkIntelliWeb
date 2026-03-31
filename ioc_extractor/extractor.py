import re

# Regex patterns for common IOCs
PATTERNS = {
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,5}",
    "crypto_wallet": r"\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b", # simplified bitcoin
    "domain": r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\b",
    "hash_md5": r"\b[a-fA-F0-9]{32}\b",
    "hash_sha256": r"\b[a-fA-F0-9]{64}\b"
}

def extract_iocs(text: str) -> list:
    iocs = []
    
    # Very basic deduplication per type
    found = set()
    
    for ioc_type, pattern in PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            val = match.group()
            # simple filter for domain to ignore common strings
            if ioc_type == 'domain' and val.lower() in ['example.com', 'test.com']:
                continue
                
            sig = f"{ioc_type}:{val}"
            if sig not in found:
                found.add(sig)
                iocs.append({
                    "type": ioc_type.replace('hash_md5', 'hash').replace('hash_sha256', 'hash'),
                    "value": val,
                    "metadata": {}
                })
                
    return iocs
