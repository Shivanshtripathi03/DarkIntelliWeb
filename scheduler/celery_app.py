import os
from celery import Celery
from celery.schedules import crontab

REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")

celery_app = Celery(
    "darkintelliweb_tasks",
    broker=REDIS_URI,
    backend=REDIS_URI,
    include=['scheduler.tasks']
)

celery_app.conf.beat_schedule = {
    'run-crawler-periodically': {
        'task': 'scheduler.tasks.run_crawling_pipeline',
        # Running every 5 minutes for demonstration purposes
        'schedule': crontab(minute='*/5'), 
    },
}
