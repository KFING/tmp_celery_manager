import asyncio
import logging

import httpx

from src.app_celery.main import app

logger = logging.getLogger(__name__)

@app.task(bind=True)
def parse_api(self, task):
    with httpx.Client() as client:
        response = client.post(f"http://localhost:50001/start", data=task, timeout=50000)
        logger.debug(response.status_code)

