import asyncio
from scheduler.celery_app import celery_app
from config.logger import setup_logger
from config.loader import load_targets
from crawler.scraper import DarkWebCrawler
from ai_engine.classifier import analyze_text
from ioc_extractor.extractor import extract_iocs
from risk_scoring.scorer import calculate_risk
from threat_intelligence.enrichment import enrich_indicator
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
                
            # Calculate Risk
            risk_score = calculate_risk(category, confidence, enriched_iocs)
            
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
            
            result = await db.threat_analysis.insert_one(analysis_doc)
            
            # Alerting
            from config.loader import load_config
            conf = load_config()
            thresh = conf.get("scoring", {}).get("high_risk_threshold", 70)
            
            if risk_score >= thresh:
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
