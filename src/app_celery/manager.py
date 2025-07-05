import json
import logging
from datetime import datetime

from pydantic import BaseModel
from redis import Redis

from src.app_celery.main import app
from celery.result import AsyncResult
from src.app_celery.tasks import parse_api
from src.dto.redis_task import RedisTask

rds = Redis()
rds.set(RedisTask.counter_of_workers.value, 3)
# Сохраняем ID текущих задач — в реальном проекте лучше использовать БД или Redis
running_tasks = {}
running_channels = {}

logger = logging.getLogger(__name__)

class TelegramTask(BaseModel):
    channel_name: str
    dt_to: datetime
    dt_from: datetime

class InvalidTelegramTask(Exception):
    pass

async def serialize_tg_task(channel_name: str) -> TelegramTask | None:
    try:
        tsk = rds.lrange(channel_name, 0, 1)
        tg_task = TelegramTask(
            channel_name=channel_name,
            dt_to=datetime.fromisoformat(tsk[0].decode("utf-8")),
            dt_from=datetime.fromisoformat(tsk[1].decode("utf-8")),
        )
        await rds.lrem(channel_name, 1, tsk[0])
        await rds.lrem(channel_name, 1, tsk[0])
        return tg_task
    except InvalidTelegramTask:
        logger.warning('Invalid TelegramTask parameters')


async def create_new_task(tsk: TelegramTask):

    global running_tasks
    global running_channels

    result = parse_api.delay(tsk)
    running_tasks[result.id] = result
    running_channels[result.id] = tsk.channel_name

    return result

@app.task
async def manager_task():

    global running_tasks
    global running_channels

    cow_redis = await rds.get(RedisTask.counter_of_workers.value)
    if isinstance(cow_redis.decode("utf-8"), str):
        cow = int(cow_redis.decode("utf-8"))
    else:
        cow = 3
    byte_channels = await rds.smembers(RedisTask.channel_name.value)
    channels = [str(channel) for channel in byte_channels]
    logger.debug(f"[{datetime.now()}] Manager is running")

    finished = [tid for tid, r in running_tasks.items() if AsyncResult(tid).ready()]

    for tid in finished:
        logger.debug(f"task finished {tid}")
        running_tasks.pop(tid)
        channel_name = running_channels.pop(tid)
        tsk = await serialize_tg_task(channel_name)
        if not tsk:
            return
        result = await create_new_task(tsk)
        logger.debug(f"Running new task: {result.id} :: {channel_name}")

    for i in range(cow - len(running_tasks.items())):
        for item in running_channels.items():
            channels.remove(str(item))
        tsk = await serialize_tg_task(channels.pop())
        result = await create_new_task(tsk)
        logger.debug(f"Running new task: {result.id} :: {channels.pop()}")
