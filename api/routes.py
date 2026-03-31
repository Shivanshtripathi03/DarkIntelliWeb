from fastapi import APIRouter, HTTPException
from typing import List
from database.db import db
from database.models import ThreatLog, Alert
from config.loader import load_targets, save_targets
from threat_intelligence.correlation import generate_threat_graph
from scheduler.tasks import run_crawling_pipeline

router = APIRouter()

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

@router.post("/scan")
async def trigger_scan():
    run_crawling_pipeline.delay()
    return {"status": "ok", "message": "Scan triggered"}

