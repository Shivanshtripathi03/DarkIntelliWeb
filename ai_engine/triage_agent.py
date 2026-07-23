import os
import json
import hashlib
from datetime import datetime, timedelta
from config.logger import setup_logger

logger = setup_logger("triage_agent")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# In-memory cache to avoid burning API quota on re-crawls of unchanged pages
_triage_cache = {}
CACHE_TTL_HOURS = 24


def _content_hash(record: dict) -> str:
    """Hash the core fields to detect duplicate content."""
    key = json.dumps({
        "url": record.get("url", ""),
        "category": record.get("threat_category", ""),
        "snippet": record.get("content_snippet", "")[:500],
        "iocs": [i.get("value") for i in record.get("extracted_indicators", [])]
    }, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()


def _is_cached(content_hash: str) -> dict | None:
    """Return cached triage result if still valid."""
    entry = _triage_cache.get(content_hash)
    if entry and datetime.utcnow() - entry["timestamp"] < timedelta(hours=CACHE_TTL_HOURS):
        logger.debug(f"Triage cache hit for {content_hash[:12]}...")
        return entry["result"]
    return None


def triage_threat(threat_record: dict) -> dict:
    """Use an LLM to autonomously triage an enriched threat record.
    
    The agent receives the full enriched record (IOCs with VT/AbuseIPDB 
    metadata, AI classification, risk score) and decides:
      - action: 'escalate' | 'monitor' | 'dismiss'
      - justification: 2-sentence reasoning
      - suggested_pivots: list of new .onion URLs worth queuing for crawl
    
    Falls back to a rule-based decision if no API key is configured or
    the API call fails.
    """
    ch = _content_hash(threat_record)
    cached = _is_cached(ch)
    if cached:
        return cached

    # Attempt LLM triage
    if ANTHROPIC_API_KEY:
        result = _llm_triage(threat_record)
    else:
        result = _rule_based_triage(threat_record)

    # Cache the result
    _triage_cache[ch] = {"result": result, "timestamp": datetime.utcnow()}
    return result


def _llm_triage(threat_record: dict) -> dict:
    """Call Claude to reason over the enriched threat bundle."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # Build a concise summary for the LLM
        summary = {
            "url": threat_record.get("url"),
            "threat_category": threat_record.get("threat_category"),
            "risk_score": threat_record.get("risk_score"),
            "confidence": threat_record.get("confidence"),
            "content_snippet": threat_record.get("content_snippet", "")[:800],
            "indicators": []
        }
        for ioc in threat_record.get("extracted_indicators", [])[:15]:
            summary["indicators"].append({
                "type": ioc.get("type"),
                "value": ioc.get("value"),
                "reputation_score": ioc.get("metadata", {}).get("reputation_score", 0),
                "malware_detections": ioc.get("metadata", {}).get("malware_detection_count", 0),
                "country": ioc.get("metadata", {}).get("country", "Unknown")
            })

        prompt = f"""You are a SOC Level 2 triage analyst for a dark web threat intelligence platform.

Analyze this enriched threat record and respond with a JSON object containing:
- "action": one of "escalate", "monitor", or "dismiss"
- "justification": exactly 2 sentences explaining your reasoning
- "suggested_pivots": array of any .onion URLs mentioned in the snippet that are worth investigating (empty array if none)

Threat Record:
{json.dumps(summary, indent=2)}

Respond with ONLY valid JSON, no markdown fences."""

        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw = resp.content[0].text.strip()
        result = json.loads(raw)
        
        # Validate expected fields
        result.setdefault("action", "monitor")
        result.setdefault("justification", "")
        result.setdefault("suggested_pivots", [])
        
        logger.info(f"LLM triage for {threat_record.get('url')}: {result['action']}")
        return result

    except Exception as e:
        logger.error(f"LLM triage failed, falling back to rules: {e}")
        return _rule_based_triage(threat_record)


def _rule_based_triage(threat_record: dict) -> dict:
    """Deterministic fallback when no API key or LLM call fails."""
    risk = threat_record.get("risk_score", 0)
    category = threat_record.get("threat_category", "unknown")
    
    # Check for high-reputation IOCs
    has_malicious_ioc = any(
        ioc.get("metadata", {}).get("malware_detection_count", 0) > 3
        for ioc in threat_record.get("extracted_indicators", [])
    )
    
    if risk >= 90 or (risk >= 70 and has_malicious_ioc):
        action = "escalate"
        justification = (
            f"Risk score {risk} with category '{category}' exceeds critical threshold. "
            f"Enrichment data confirms malicious indicators warranting immediate attention."
        )
    elif risk >= 50:
        action = "monitor"
        justification = (
            f"Risk score {risk} in category '{category}' is moderate. "
            f"Continued monitoring recommended pending additional corroborating evidence."
        )
    else:
        action = "dismiss"
        justification = (
            f"Risk score {risk} for '{category}' is below actionable thresholds. "
            f"No significant malicious indicators found in enrichment data."
        )

    return {
        "action": action,
        "justification": justification,
        "suggested_pivots": []
    }
