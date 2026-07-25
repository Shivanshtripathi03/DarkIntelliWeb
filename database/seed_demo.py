import asyncio
from datetime import datetime, timedelta
from database.db import db
from config.logger import setup_logger

logger = setup_logger("seed_demo")

SAMPLE_THREATS = [
    {
        "url": "http://lockbit37462x7z8a.onion/leaks/corp_vault_2026",
        "timestamp": datetime.utcnow() - timedelta(hours=2),
        "risk_score": 92,
        "threat_category": "ransomware activity",
        "confidence": 0.94,
        "is_synthetic": True,
        "content_snippet": "LockBit 3.0 Leak Site: Exfiltrated 450GB internal SQL database dumps, finance records, and private keys. Target company failed negotiation window.",
        "extracted_indicators": [
            {"type": "ip", "value": "185.220.101.5", "metadata": {"country": "RU", "malware_detection_count": 8, "reputation_score": 85}},
            {"type": "crypto_wallet", "value": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "metadata": {"enriched": True}},
            {"type": "hash", "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "metadata": {"malware_detection_count": 14, "reputation_score": 90}}
        ],
        "triage": {
            "action": "escalate",
            "justification": "Risk score 92 in ransomware activity with multiple malicious IOCs confirmed across threat feeds.",
            "suggested_pivots": ["http://blackcat77a29xzb.onion"]
        }
    },
    {
        "url": "http://carderhub998xa7z.onion/market/cvv-dumps",
        "timestamp": datetime.utcnow() - timedelta(hours=5),
        "risk_score": 81,
        "threat_category": "carding marketplaces",
        "confidence": 0.88,
        "is_synthetic": True,
        "content_snippet": "Fresh US/EU Visa & MasterCard dumps with PIN. Fullz included. Auto-checker enabled. Bulk discount available for crypto.",
        "extracted_indicators": [
            {"type": "ip", "value": "194.26.29.110", "metadata": {"country": "CN", "malware_detection_count": 5, "reputation_score": 70}},
            {"type": "email", "value": "admin@carderhub.onion", "metadata": {"enriched": True}},
            {"type": "domain", "value": "carderhub-checkout.com", "metadata": {"malware_detection_count": 3, "reputation_score": 60}}
        ],
        "triage": {
            "action": "escalate",
            "justification": "Active financial carding marketplace selling stolen payment card batches.",
            "suggested_pivots": []
        }
    },
    {
        "url": "http://breachforums827z.onion/thread-29401",
        "timestamp": datetime.utcnow() - timedelta(hours=8),
        "risk_score": 88,
        "threat_category": "data breaches",
        "confidence": 0.91,
        "is_synthetic": True,
        "content_snippet": "Selling 12 Million user records including hashed passwords, emails, SSNs, and birth dates. Escrow via Telegram admin.",
        "extracted_indicators": [
            {"type": "ip", "value": "185.106.92.24", "metadata": {"country": "IR", "malware_detection_count": 6, "reputation_score": 75}},
            {"type": "email", "value": "leak_broker@proton.me", "metadata": {"enriched": True}},
            {"type": "crypto_wallet", "value": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "metadata": {"enriched": True}}
        ],
        "triage": {
            "action": "escalate",
            "justification": "Massive user credential breach database put up for public auction.",
            "suggested_pivots": []
        }
    },
    {
        "url": "http://zero-day-bazaar.onion/exploits/ios-kernel-rce",
        "timestamp": datetime.utcnow() - timedelta(hours=12),
        "risk_score": 76,
        "threat_category": "exploit trading",
        "confidence": 0.85,
        "is_synthetic": True,
        "content_snippet": "Unpatched zero-day remote code execution vulnerability chain for modern webkit/kernel. Proof of concept available upon proof of funds.",
        "extracted_indicators": [
            {"type": "ip", "value": "193.106.191.22", "metadata": {"country": "US", "malware_detection_count": 2, "reputation_score": 40}},
            {"type": "hash", "value": "5d41402abc4b2a76b9719d911017c592", "metadata": {"malware_detection_count": 7, "reputation_score": 75}}
        ],
        "triage": {
            "action": "monitor",
            "justification": "Unverified 0-day exploit claims require technical verification before escalating.",
            "suggested_pivots": []
        }
    },
    {
        "url": "http://darknet-botnet-panel.onion/dashboard",
        "timestamp": datetime.utcnow() - timedelta(hours=18),
        "risk_score": 68,
        "threat_category": "botnet services",
        "confidence": 0.82,
        "is_synthetic": True,
        "content_snippet": "Mirai variant botnet for hire. Guaranteed 400 Gbps UDP/SYN flood capability. Stress testing packages starting at $50/hour.",
        "extracted_indicators": [
            {"type": "ip", "value": "177.12.98.41", "metadata": {"country": "BR", "malware_detection_count": 4, "reputation_score": 65}}
        ],
        "triage": {
            "action": "monitor",
            "justification": "DDoS booter panel offering botnet stress testing services.",
            "suggested_pivots": []
        }
    }
]

async def seed():
    db.reset()
    count = await db.threat_analysis.count_documents({})
    if count == 0:
        logger.info("Seeding initial synthetic threat intelligence data into MongoDB...")
        await db.threat_analysis.insert_many(SAMPLE_THREATS)
        
        # Add a critical alert for high risk items
        for t in SAMPLE_THREATS:
            if t["risk_score"] >= 85:
                alert = {
                    "threat_log_id": "seed_" + t["threat_category"].replace(" ", "_"),
                    "timestamp": t["timestamp"],
                    "level": "CRITICAL",
                    "message": f"High risk threat detected at {t['url']}: {t['threat_category']} with score {t['risk_score']}",
                    "read": False
                }
                await db.alerts.insert_one(alert)
        logger.info("Database successfully seeded with demo telemetry.")
    else:
        logger.info(f"Database already contains {count} threat analysis records.")

if __name__ == "__main__":
    asyncio.run(seed())
