import json

from redis import Redis

from src.app_celery.main import app
from celery.result import AsyncResult
from src.app_celery.tasks import parse_api
import datetime
rds = Redis()
rds.set('N', 3)
# Сохраняем ID текущих задач — в реальном проекте лучше использовать БД или Redis
running_tasks = {}

@app.task
def manager_task():
    global running_tasks
    n = int(rds.get('N'))
    elem = json.loads(rds.spop('task_set'))
    print(f"[{datetime.datetime.now()}] Manager is running")

    # Удалим завершённые задачи из слежения
    finished = [tid for tid, r in running_tasks.items() if AsyncResult(tid).ready()]
    for tid in finished:
        print(f"task finished {tid}")
        running_tasks.pop(tid)
        elem = json.loads(rds.spop('task_set'))
        result = parse_api.delay(elem)
        running_tasks[result.id] = result
        print(f"Running new task: {result.id}")

    if running_tasks:
        return

    for i in range(n):
        elem = json.loads(rds.spop('task_set'))
        result = parse_api.delay(elem)
        running_tasks[result.id] = result
        print(f"Running new task: {result.id}")
