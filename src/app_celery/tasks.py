import httpx

from src.app_celery.main import app
import time
import random

from src.app_celery.manager import TelegramTask


@app.task(bind=True)
async def parse_api(self, task: TelegramTask):
    async with httpx.AsyncClient() as client:

        # POST запрос
        data = {"channel_name": task.channel_name, "dt_to": str(task.dt_to), "dt_from": str(task.dt_from)}
        response = await client.post(f"http://localhost:50001/start/", json=data)
        print(response.status_code)
        print(response.json())

