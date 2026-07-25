import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.loader import load_config

REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")

celery_app = Celery(
    "darkintelliweb_tasks",
    broker=REDIS_URI,
    backend=REDIS_URI,
    include=['scheduler.tasks']
)

# Load dynamic crawl interval from config
config = load_config()
interval_minutes = config.get("crawler", {}).get("crawl_interval_minutes", 360)

celery_app.conf.beat_schedule = {
    'run-crawler-periodically': {
        'task': 'scheduler.tasks.run_crawling_pipeline',
        'schedule': timedelta(minutes=float(interval_minutes)),
    },
}
