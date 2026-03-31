import asyncio
from datetime import datetime
import motor.motor_asyncio
import os
import random
import sys
from pathlib import Path

# Fix relative imports when run standalone
sys.path.append(str(Path(__file__).resolve().parent.parent))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.darkintelliweb

MOCK_TEXTS = [
    "We have breached a major bank. Database dumps available, contact via jabber. IPs: 192.168.1.5, 10.0.0.1",
    "Selling botnet access. 10k nodes. Email me at admin@darkbot.net",
    "Ransomware decryptor keys for sale. Send 0.5 to bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "Leaked credentials from example.com. Hash: d41d8cd98f00b204e9800998ecf8427e",
    "New carding marketplace open at http://cards123.onion."
]

CATEGORIES = ["data breaches", "botnet services", "ransomware activity", "credential dumps", "carding marketplaces"]

async def populate_mock_data():
    print("Clearing old data...")
    await db.raw_pages.delete_many({})
    await db.threat_analysis.delete_many({})
    await db.alerts.delete_many({})
    
    print("Generating mock threats...")
    for i in range(50):
        cat = random.choice(CATEGORIES)
        text = random.choice(MOCK_TEXTS)
        url = f"http://mock{random.randint(1,20)}.onion"
        
        doc = {
            "url": url,
            "timestamp": datetime.utcnow(),
            "risk_score": random.randint(40, 95),
            "threat_category": cat,
            "confidence": round(random.uniform(0.6, 0.99), 2),
            "content_snippet": text,
            "extracted_indicators": [
                {"type": "ip", "value": f"{random.randint(1,255)}.{random.randint(1,255)}.1.1", "metadata": {"country": random.choice(["RU", "CN", "KP", "IR", "US"])}},
                {"type": "domain", "value": f"malicious{random.randint(1,10)}.com", "metadata": {}}
            ]
        }
        res = await db.threat_analysis.insert_one(doc)
        
        if doc["risk_score"] > 80:
            await db.alerts.insert_one({
                "threat_log_id": str(res.inserted_id),
                "timestamp": datetime.utcnow(),
                "level": "CRITICAL" if doc["risk_score"] > 90 else "HIGH",
                "message": f"High risk threat detected at {url}: {cat}",
                "read": False
            })
            
    print("Populated mock data successfully.")

if __name__ == "__main__":
    asyncio.run(populate_mock_data())
