import logging

import httpx

from src.app_celery.main import app
from src.dto.redis_task import TelegramTask

logger = logging.getLogger(__name__)

@app.task(bind=True)
def parse_api(self, task):
    with httpx.Client() as client:

        data = {
            "channel_name": task.channel_name,
            "dt_to": str(task.dt_to),
            "dt_from": str(task.dt_from)
        }

        response = client.post(f"http://localhost:50001/start/", json=data)
        logger.debug(response.status_code)
        logger.debug(response.json())

