import asyncio
import logging
from datetime import datetime

import httpx
from pydantic import HttpUrl

from src.app_celery.main import app
from src.db_main.cruds import tg_post_crud
from src.dto.redis_task import TelegramTask
from src.dto.tg_post import TgPost
from src.env import SCRAPPER_TMP_MEDIA_DIR__TELEGRAM

logger = logging.getLogger(__name__)

class InvalidDataException(Exception):
    pass

def heapify(arr: list[TgPost], n: int, i: int):
    largest = i # Initialize largest as root
    l = 2 * i + 1   # left = 2*i + 1
    r = 2 * i + 2   # right = 2*i + 2

  # Проверяем существует ли левый дочерний элемент больший, чем корень

    if l < n and arr[i].pb_date < arr[l].pb_date:
        largest = l

    # Проверяем существует ли правый дочерний элемент больший, чем корень

    if r < n and arr[largest].pb_date < arr[r].pb_date:
        largest = r

    # Заменяем корень, если нужно
    if largest != i:
        arr[i],arr[largest] = arr[largest],arr[i] # свап

        # Применяем heapify к корню.
        heapify(arr, n, largest)

# Основная функция для сортировки массива заданного размера
def heap_sort(arr: list[TgPost]):
    n = len(arr)

    # Построение max-heap.
    for i in range(n, -1, -1):
        heapify(arr, n, i)

    # Один за другим извлекаем элементы
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)

def save_to_telegram_file(posts: list[TgPost]):
    heap_sort(posts)
    tmp_posts: list[TgPost] = []
    for post in posts:
        tmp_post = tmp_posts[-1]
        if len(tmp_list) == 0:
            tmp_list.append(task)
            continue
        if
        (SCRAPPER_TMP_MEDIA_DIR__TELEGRAM / task.tg_channel_id / f"{task.pb_date.year}" / f"{task.tg_channel_id}_{task.tg_post_id}__{task.pb_date.month}.json").write_text(task.model_dump_json(indent=4))

def parse_data(channel_name: str, posts: list[dict[str, str]], *, log_extra: dict[str, str]) -> list[TgPost | None]:
    tg_posts: list[TgPost] = []
    try:
        for post in posts:
            tg_posts.append(TgPost(tg_channel_id=post['tg_channel_id'],
                                    tg_post_id=int(post['tg_post_id']),
                                    content=post['content'],
                                    pb_date=datetime.fromisoformat(post['pb_date']),
                                    link=HttpUrl(post['link'])))
    except InvalidDataException as e:
        logger.warning(f'CELERY WORKER :: invalid response data for channel -- {channel_name} -- {e}', extra=log_extra)
    return tg_posts

@app.task(bind=True)
def parse_api(self, task: TelegramTask, *, log_extra: dict[str, str]) -> None:
    with httpx.Client() as client:
        response = client.post(f"http://localhost:50001/start", data=task.model_dump_json(indent=4), timeout=10000)
        logger.debug(response.status_code)
        if response.status_code != 200:
            return
    tg_posts = parse_data(task.channel_name, response.json(), log_extra=log_extra)

    # posts = await tg_post_crud.create_tg_posts(db, tg_posts)




