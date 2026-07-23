import asyncio
from scheduler.celery_app import celery_app
from config.logger import setup_logger
from config.loader import load_targets
from crawler.scraper import DarkWebCrawler
from ai_engine.classifier import analyze_text
from ioc_extractor.extractor import extract_iocs
from risk_scoring.scorer import calculate_risk, calculate_risk_with_triage
from threat_intelligence.enrichment import enrich_indicator
from config.loader import load_targets, load_config, save_targets
from database.db import db
from datetime import datetime

logger = setup_logger("celery_tasks")

@celery_app.task
def run_crawling_pipeline():
    """Celery task to run the async crawler in sync bridge"""
    logger.info("Starting scheduled crawling pipeline...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_crawling_pipeline())
    finally:
        loop.close()
        
    logger.info("Completed scheduled crawling pipeline.")

async def _async_crawling_pipeline():
    # Force Motor to bind to the fresh loop created by celery
    db.reset()
    targets = load_targets()
    if not targets:
        logger.warning("No targets found to crawl. Exiting pipeline.")
        return

    crawler = DarkWebCrawler(targets)
    await crawler.run()
    
    # Process unanalyzed raw HTML pages
    await process_raw_pages()

async def process_raw_pages():
    cursor = db.raw_pages.find({"processed": False})
    
    async for page in cursor:
        try:
            url = page["url"]
            text = page.get("text", "")
            
            # AI Inference (CPU bound, run in thread)
            ai_result = await asyncio.to_thread(analyze_text, text)
            category = ai_result["category"]
            confidence = ai_result["confidence"]
            
            # Extract IOCs (CPU bound regex, run in thread)
            iocs = await asyncio.to_thread(extract_iocs, text)
            
            # Enrich IOCs
            enriched_iocs = []
            for ioc in iocs:
                meta = await enrich_indicator(ioc["type"], ioc["value"])
                ioc["metadata"] = meta
                enriched_iocs.append(ioc)
                
            # Calculate Risk with optional autonomous triage
            risk_result = await asyncio.to_thread(
                calculate_risk_with_triage,
                category, confidence, enriched_iocs,
                {"url": url, "content_snippet": text[:500]}
            )
            risk_score = risk_result["risk_score"]
            triage = risk_result.get("triage")
            
            # Store Threat Analysis
            analysis_doc = {
                "url": url,
                "timestamp": datetime.utcnow(),
                "risk_score": risk_score,
                "threat_category": category,
                "confidence": confidence,
                "extracted_indicators": enriched_iocs,
                "content_snippet": text[:500]
            }
            
            # Attach triage decision if available
            if triage:
                analysis_doc["triage"] = triage
            
            result = await db.threat_analysis.insert_one(analysis_doc)
            
            # Handle autonomous pivot suggestions (queue new .onion URLs)
            if triage and triage.get("suggested_pivots"):
                current_targets = load_targets()
                for pivot_url in triage["suggested_pivots"]:
                    if pivot_url not in current_targets and ".onion" in pivot_url:
                        current_targets.append(pivot_url)
                        logger.info(f"Triage agent queued new target: {pivot_url}")
                save_targets(current_targets)
            
            # Alerting
            conf = load_config()
            thresh = conf.get("scoring", {}).get("high_risk_threshold", 70)
            
            # Use triage action for alert level when available
            if triage and triage.get("action") == "escalate":
                alert_level = "CRITICAL"
                alert_msg = f"[TRIAGE: ESCALATE] {triage.get('justification', '')} | {url}"
                alert = {
                    "threat_log_id": str(result.inserted_id),
                    "timestamp": datetime.utcnow(),
                    "level": alert_level,
                    "message": alert_msg,
                    "read": False
                }
                await db.alerts.insert_one(alert)
                logger.warning(f"ALERT: {alert['message']}")
            elif risk_score >= thresh:
                alert = {
                    "threat_log_id": str(result.inserted_id),
                    "timestamp": datetime.utcnow(),
                    "level": "CRITICAL" if risk_score >= 90 else "HIGH",
                    "message": f"High risk threat detected at {url}: {category} with score {risk_score}",
                    "read": False
                }
                await db.alerts.insert_one(alert)
                logger.warning(f"ALERT: {alert['message']}")
            
            # Mark processed
            await db.raw_pages.update_one({"_id": page["_id"]}, {"$set": {"processed": True}})
            
        except Exception as e:
            logger.error(f"Error processing page {page.get('url')}: {str(e)}")
