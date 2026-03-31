from config.loader import load_config

config = load_config()
severity_map = config.get("categories_severity", {})
weights = config.get("scoring", {}).get("weights", {
    "ai_confidence": 0.4,
    "category_severity": 0.4,
    "indicator_criticality": 0.2
})

def calculate_risk(category: str, confidence: float, iocs: list) -> int:
    # Get base severity, default to 50 if unknown
    severity = severity_map.get(category, 50)
    
    # Evaluate indicator criticality
    # e.g., having a crypto wallet or an ip usually indicates higher risk in dark web context
    ioc_score = 0
    types_found = set([i["type"] for i in iocs])
    
    if "crypto_wallet" in types_found:
        ioc_score += 40
    if "hash" in types_found:
        ioc_score += 30
    if "ip" in types_found or "domain" in types_found:
        ioc_score += 20
    if "email" in types_found:
        ioc_score += 10
        
    ioc_score = min(ioc_score, 100) # cap at 100
    
    # Calculate final score
    score_float = (
        (severity * weights.get("category_severity", 0.4)) +
        (confidence * 100 * weights.get("ai_confidence", 0.4)) +
        (ioc_score * weights.get("indicator_criticality", 0.2))
    )
    
    return int(min(max(score_float, 0), 100))
