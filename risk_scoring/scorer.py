from config.loader import load_config
from config.logger import setup_logger

logger = setup_logger("scorer")
config = load_config()
severity_map = config.get("categories_severity", {})
weights = config.get("scoring", {}).get("weights", {
    "ai_confidence": 0.4,
    "category_severity": 0.4,
    "indicator_criticality": 0.2
})

def calculate_risk(category: str, confidence: float, iocs: list) -> int:
    """Calculate composite risk score from AI confidence, category severity, and IOC types."""
    # Get base severity, default to 50 if unknown
    severity = severity_map.get(category, 50)
    
    # Evaluate indicator criticality
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
        
    ioc_score = min(ioc_score, 100)  # cap at 100
    
    # Calculate final score
    score_float = (
        (severity * weights.get("category_severity", 0.4)) +
        (confidence * 100 * weights.get("ai_confidence", 0.4)) +
        (ioc_score * weights.get("indicator_criticality", 0.2))
    )
    
    return int(min(max(score_float, 0), 100))


def calculate_risk_with_triage(category: str, confidence: float, iocs: list, threat_record: dict) -> dict:
    """Calculate risk score AND run autonomous triage.
    
    Returns a dict with 'risk_score' and 'triage' (action/justification/pivots).
    """
    risk_score = calculate_risk(category, confidence, iocs)
    
    triage_config = config.get("triage", {})
    triage_result = None
    
    if triage_config.get("enabled", False):
        try:
            from ai_engine.triage_agent import triage_threat
            enriched_record = {
                **threat_record,
                "risk_score": risk_score,
                "threat_category": category,
                "confidence": confidence,
                "extracted_indicators": iocs
            }
            triage_result = triage_threat(enriched_record)
            logger.info(f"Triage decision: {triage_result.get('action')} for {threat_record.get('url')}")
        except Exception as e:
            logger.error(f"Triage agent error: {e}")
    
    return {
        "risk_score": risk_score,
        "triage": triage_result
    }
