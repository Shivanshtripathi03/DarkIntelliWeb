import asyncio
import aiohttp
import base64
from config.loader import load_config
from config.logger import setup_logger

logger = setup_logger("enrichment")
config = load_config()

# Read API keys safely
APIS = config.get("apis", {})
ABUSEIPDB_KEY = APIS.get("abuseipdb", "")
VIRUSTOTAL_KEY = APIS.get("virustotal", "")

async def fetch_abuseipdb(session: aiohttp.ClientSession, ip: str) -> dict:
    if not ABUSEIPDB_KEY:
        return {}
        
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": ABUSEIPDB_KEY
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": "90"
    }
    try:
        async with session.get(url, headers=headers, params=params, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
            else:
                logger.warning(f"AbuseIPDB failed for {ip}: {response.status}")
    except Exception as e:
        logger.error(f"AbuseIPDB request error for {ip}: {e}")
    return {}

async def fetch_virustotal(session: aiohttp.ClientSession, endpoint: str) -> dict:
    if not VIRUSTOTAL_KEY:
        return {}
        
    url = f"https://www.virustotal.com/api/v3/{endpoint}"
    headers = {
        "x-apikey": VIRUSTOTAL_KEY
    }
    try:
        async with session.get(url, headers=headers, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            else:
                logger.warning(f"VirusTotal failed for {endpoint}: {response.status}")
    except Exception as e:
        logger.error(f"VirusTotal request error for {endpoint}: {e}")
    return {}

async def enrich_indicator(ioc_type: str, value: str) -> dict:
    """
    Enrich an indicator of compromise using AbuseIPDB and VirusTotal APIs.
    Gracefully falls back to 0 detections if keys are missing or requests fail.
    """
    metadata = {
        "enriched": True,
        "reputation_score": 0,
        "malware_detection_count": 0
    }
    
    async with aiohttp.ClientSession() as session:
        if ioc_type == "ip":
            # Run both AbuseIPDB and VirusTotal in parallel
            vt_task = fetch_virustotal(session, f"ip_addresses/{value}")
            abuse_task = fetch_abuseipdb(session, value)
            vt_stats, abuse_data = await asyncio.gather(vt_task, abuse_task)
            
            # Combine results
            metadata["malware_detection_count"] = vt_stats.get("malicious", 0) + vt_stats.get("suspicious", 0)
            metadata["abuseipdb_score"] = abuse_data.get("abuseConfidenceScore", 0)
            metadata["country"] = abuse_data.get("countryCode", "Unknown")
            metadata["isp"] = abuse_data.get("isp", "Unknown")
            
            # Synthesize reputation score (0-100)
            metadata["reputation_score"] = metadata["abuseipdb_score"]
            
        elif ioc_type == "domain":
            vt_stats = await fetch_virustotal(session, f"domains/{value}")
            metadata["malware_detection_count"] = vt_stats.get("malicious", 0) + vt_stats.get("suspicious", 0)
            
            # Dummy score based on detections
            metadata["reputation_score"] = min(100, metadata["malware_detection_count"] * 10)
            
        elif ioc_type == "hash":
            vt_stats = await fetch_virustotal(session, f"files/{value}")
            metadata["malware_detection_count"] = vt_stats.get("malicious", 0) + vt_stats.get("suspicious", 0)
            metadata["reputation_score"] = min(100, metadata["malware_detection_count"] * 10)
            
        elif ioc_type == "url":
            # VT v3 urls require base64 without padding
            url_id = base64.urlsafe_b64encode(value.encode()).decode().strip("=")
            vt_stats = await fetch_virustotal(session, f"urls/{url_id}")
            metadata["malware_detection_count"] = vt_stats.get("malicious", 0) + vt_stats.get("suspicious", 0)
            metadata["reputation_score"] = min(100, metadata["malware_detection_count"] * 10)
            
    return metadata
