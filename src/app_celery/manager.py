from src.app_celery.main import app
from celery.result import AsyncResult
from src.app_celery.tasks import parse_api
import datetime

# Сохраняем ID текущих задач — в реальном проекте лучше использовать БД или Redis
running_tasks = {}

@app.task
def manager_task():
    global running_tasks

    print(f"[{datetime.datetime.now()}] Менеджер запущен")

    # Удалим завершённые задачи из слежения
    finished = [tid for tid, r in running_tasks.items() if AsyncResult(tid).ready()]
    for tid in finished:
        print(f"Задача {tid} завершена")
        running_tasks.pop(tid)

    if running_tasks:
        print("Есть незавершённые задачи. Ждём следующего запуска.")
        return

    # Здесь — логика генерации новых заданий
    for i in range(3):  # например, три новых запроса
        url = "https://api.example.com/data"
        params = {"q": f"item{i}", "page": 1}
        result = parse_api.delay(url, params)
        running_tasks[result.id] = result
        print(f"Запущена новая задача: {result.id}")
