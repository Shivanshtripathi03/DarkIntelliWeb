import re
import tldextract

# Regex patterns for common IOCs
PATTERNS = {
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,5}",
    "crypto_wallet": r"\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b",  # simplified bitcoin
    "domain": r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\b",
    "hash_md5": r"\b[a-fA-F0-9]{32}\b",
    "hash_sha256": r"\b[a-fA-F0-9]{64}\b"
}

# Known non-IOC patterns to skip
_SKIP_DOMAINS = {"example.com", "test.com", "localhost", "w3.org", "schema.org", "xmlns.com"}


def _is_valid_domain(candidate: str) -> bool:
    """Validate that a matched string is a real domain using tldextract."""
    if candidate.lower() in _SKIP_DOMAINS:
        return False
    ext = tldextract.extract(candidate)
    # Must have a real registered domain AND a known public suffix
    return bool(ext.domain and ext.suffix)


def _is_valid_ip(candidate: str) -> bool:
    """Check that each octet is in 0-255 range."""
    parts = candidate.split(".")
    return all(0 <= int(p) <= 255 for p in parts)


def extract_iocs(text: str) -> list:
    """Extract Indicators of Compromise from text with validation."""
    iocs = []
    found = set()  # deduplication

    for ioc_type, pattern in PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            val = match.group()

            # Domain validation via tldextract
            if ioc_type == "domain" and not _is_valid_domain(val):
                continue

            # IP validation - octets must be 0-255
            if ioc_type == "ip":
                try:
                    if not _is_valid_ip(val):
                        continue
                except (ValueError, IndexError):
                    continue

            sig = f"{ioc_type}:{val}"
            if sig not in found:
                found.add(sig)
                iocs.append({
                    "type": ioc_type.replace("hash_md5", "hash").replace("hash_sha256", "hash"),
                    "value": val,
                    "metadata": {}
                })

    return iocs
