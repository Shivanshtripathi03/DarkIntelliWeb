from transformers import pipeline
from config.loader import load_config
from config.logger import setup_logger

logger = setup_logger("ai_engine")
config = load_config()

# categories from config
categories = list(config.get("categories_severity", {}).keys())
if not categories:
    categories = [
        "data breaches", "ransomware activity", "malware marketplaces",
        "exploit trading", "credential dumps", "botnet services",
        "hacking services", "carding marketplaces", "stolen databases"
    ]

# Initialize pipeline lazily to save memory if not used immediately
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        logger.info("Loading Zero-Shot Classification Model...")
        try:
            # Setting device=-1 forces CPU which avoids some CUDA initialization issues in docker
            _classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3", device=-1)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            _classifier = "keyword_fallback"
    return _classifier

def analyze_text(text: str) -> dict:
    if not text or len(text.strip()) < 10:
        return {"category": "unknown", "confidence": 0.0}
    
    # Truncate text to avoid token limit errors (typically 512 tokens max for BERT-like)
    # roughly 2000 chars is safe
    safe_text = text[:2000]
    
    classifier = get_classifier()
    
    if classifier == "keyword_fallback" or classifier is None:
        # Simple keyword fallback if HF model fails to download due to rate limits
        lower_text = text.lower()
        best_cat = "unknown"
        best_conf = 0.0
        kw_map = {
            "stolen databases": ["leak", "database", "sql", "dump", "breach"],
            "hacking services": ["hack", "exploit", "0day", "ddos", "botnet", "ransom"],
            "carding marketplaces": ["card", "cvv", "fullz", "dump", "stripe", "cc"],
            "malware marketplaces": ["malware", "trojan", "stealer", "rat", "virus"]
        }
        for cat, kws in kw_map.items():
            if any(kw in lower_text for kw in kws):
                if best_conf == 0.0:
                    best_cat = cat
                    best_conf = 0.60
                break
        return {"category": best_cat, "confidence": best_conf}

    try:
        result = classifier(safe_text, candidate_labels=categories)
        # result contains 'labels' and 'scores' sorted by highest score
        top_category = result['labels'][0]
        top_score = result['scores'][0]
        return {
            "category": top_category,
            "confidence": top_score
        }
    except Exception as e:
        logger.error(f"Error in AI classification: {str(e)}")
        return {"category": "error", "confidence": 0.0}
