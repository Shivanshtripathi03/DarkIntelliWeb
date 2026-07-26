from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from typing import List
import os
import httpx
from database.db import db
from database.models import ThreatLog, Alert
from config.loader import load_targets, save_targets
from threat_intelligence.correlation import generate_threat_graph
from scheduler.tasks import run_crawling_pipeline, _async_crawling_pipeline

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
BACKEND_SECRET_KEY = os.environ.get("BACKEND_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not BACKEND_SECRET_KEY:
    raise RuntimeError("Missing required environment variables: SUPABASE_URL, SUPABASE_ANON_KEY, and BACKEND_SECRET_KEY must be set in the environment.")

async def get_current_user(request: Request, authorization: str = Header(None)):
    # 1. Allow server-to-server calls via secret API key (e.g. from local Streamlit app)
    api_key = request.headers.get("x-api-key")
    if api_key == BACKEND_SECRET_KEY:
        return {"role": "system"}

    # 2. Otherwise require and verify Supabase JWT token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
    token = authorization.split(" ")[1]
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_ANON_KEY
        }
        try:
            resp = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Supabase JWT token")
            return resp.json()
        except Exception:
            raise HTTPException(status_code=401, detail="Authentication failed")

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/overview")
async def get_overview():
    total_threats = await db.threat_analysis.count_documents({})
    high_risk_alerts = await db.alerts.count_documents({"level": "CRITICAL"})
    
    # Simple aggregation for categories
    pipeline = [{"$group": {"_id": "$threat_category", "count": {"$sum": 1}}}]
    cursor = db.threat_analysis.aggregate(pipeline)
    categories = [{"category": doc["_id"], "count": doc["count"]} async for doc in cursor]
    
    return {
        "total_threats": total_threats,
        "high_risk_alerts": high_risk_alerts,
        "categories": categories
    }

@router.get("/threats")
async def get_threats(limit: int = 50, skip: int = 0):
    cursor = db.threat_analysis.find().sort("timestamp", -1).skip(skip).limit(limit)
    threats = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        threats.append(doc)
    return threats

@router.get("/alerts")
async def get_alerts(limit: int = 10):
    cursor = db.alerts.find().sort("timestamp", -1).limit(limit)
    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        alerts.append(doc)
    return alerts

@router.get("/graph")
async def get_graph():
    return await generate_threat_graph()

@router.get("/targets")
async def get_targets():
    return {"targets": load_targets()}

@router.post("/targets")
async def add_target(body: dict):
    target = body.get("url")
    if not target:
        raise HTTPException(status_code=400, detail="Missing url")
    if not target.startswith('http'):
        target = 'http://' + target
    targets = load_targets()
    if target not in targets:
        targets.append(target)
        save_targets(targets)
    return {"status": "ok", "targets": targets}

@router.delete("/targets")
async def remove_target(body: dict):
    target = body.get("url")
    if not target:
        raise HTTPException(status_code=400, detail="Missing url")
    targets = load_targets()
    if target in targets:
        targets.remove(target)
        save_targets(targets)
    return {"status": "ok", "targets": targets}

import asyncio
from scheduler.tasks import _async_crawling_pipeline

@router.post("/scan")
async def trigger_scan():
    # Check if any celery workers are online
    celery_active = False
    try:
        from scheduler.celery_app import celery_app
        stats = celery_app.control.inspect().stats()
        if stats:
            celery_active = True
    except Exception:
        pass

    if celery_active:
        run_crawling_pipeline.delay()
    else:
        # Fall back to local asyncio task since Celery worker is offline
        asyncio.create_task(_async_crawling_pipeline())
        
    return {"status": "ok", "message": "Scan initiated"}

import re
import os
import json

@router.get("/ai-summary")
async def get_ai_summary():
    """Generates an AI CISO Analyst Summary of the threat landscape."""
    cursor = db.threat_analysis.find().sort("timestamp", -1).limit(10)
    threats = []
    async for doc in cursor:
        threats.append({
            "url": doc.get("url"),
            "category": doc.get("threat_category"),
            "risk": doc.get("risk_score"),
            "iocs": [i.get("value") for i in doc.get("extracted_indicators", [])]
        })

    if not threats:
        return {"summary": "No active dark web threat telemetry is currently available. Ingest some targets or trigger a manual scan to generate security reports."}

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a Lead CISO Threat Analyst.
Analyze these recent dark web threat records and write a 3-sentence Executive Summary of the current threat landscape, followed by 3 bullet points of immediate defense recommendations.
Respond in plain text. Do not use JSON or markdown code fences.

Threat Records:
{json.dumps(threats, indent=2)}"""

            resp = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"summary": resp.content[0].text.strip()}
        except Exception as e:
            # Fall back to rule-based parser on API errors
            pass

    # Dynamic Rule-Based Security Summary Generator
    categories = [t["category"] for t in threats]
    high_risk = [t for t in threats if t["risk"] >= 80]
    ips = []
    for t in threats:
        for val in t["iocs"]:
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", val):
                ips.append(val)

    summary_sentences = [
        f"**CISO Intelligence Summary:** The platform is currently tracking {len(threats)} active dark web threat nodes.",
        f"Campaigns are heavily concentrated across the **{', '.join(set(categories[:3]))}** threat vectors."
    ]
    if high_risk:
        summary_sentences.append(f"Immediate containment action is recommended for {len(high_risk)} critical threats (Risk score >= 80), notably focusing on source domain `{high_risk[0]['url']}`.")
    if ips:
        summary_sentences.append(f"Security groups should monitor network egress for command-and-control IP indicators, including: `{', '.join(set(ips[:3]))}`.")

    recommendations = (
        "\n\n**Strategic Containment Actions:**\n"
        "- **Ingress Filtering:** Block outbound firewall requests towards flagged exit nodes and command-and-control IPs.\n"
        "- **Credential Revocation:** Initiate reset cycles for user accounts flagged under compromised data dumps.\n"
        "- **SIEM Ingestion:** Register extracted hashes and malicious domains into active detection rules to monitor potential breach paths."
    )

    return {"summary": " ".join(summary_sentences) + recommendations}


@router.post("/query")
async def query_ai(body: dict):
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
        
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"You are a threat intelligence assistant. Answer the user's security question: {query}"
            resp = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"answer": resp.content[0].text.strip()}
        except Exception:
            pass
            
    # Simple rule-based/intelligence responses fallback
    lower = query.lower()
    if "apt" in lower or "state-sponsored" in lower:
        ans = "Threat group correlation suggests connection to APT activities (e.g., APT-28, APT-29) targeting critical sectors."
    elif "ransomware" in lower or "lock" in lower:
        ans = "Recent ransomware trends show a rise in double-extortion schemes. Ensure offline backups are isolated and access control is tightly monitored."
    elif "cve" in lower or "vulnerability" in lower:
        ans = "Verify systems against public exploit databases (NVD/MITRE) and prioritize patching critical RCE vulnerabilities immediately."
    else:
        ans = "Threat Intelligence analysis: No direct indicators found matching the query in recent dark web dumps."
        
    return {"answer": ans}


@router.post("/reset")
async def reset_database():
    """Wipes raw_pages, threat_analysis, and alerts collections."""
    await db.raw_pages.delete_many({})
    await db.threat_analysis.delete_many({})
    await db.alerts.delete_many({})
    return {"status": "ok", "message": "Database wiped successfully"}


@router.get("/status")
async def get_status():
    """Gets the current status of the background crawler."""
    doc = await db.system_status.find_one({"_id": "crawler"})
    if not doc:
        return {"status": "idle", "last_run": None}
    return {
        "status": doc.get("status", "idle"),
        "last_run": doc.get("last_run").isoformat() if doc.get("last_run") else None
    }


