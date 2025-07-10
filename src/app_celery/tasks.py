import asyncio
import json
import logging
from datetime import datetime

import httpx
from pydantic import HttpUrl, BaseModel

from src.app_api.dependencies import get_db_main_manager, get_db_main
from src.app_celery.main import app
from src.common.async_utils import run_on_loop
from src.db_main.cruds import tg_post_crud
from src.dto.redis_task import TelegramTask
from src.dto.tg_post import TgPost
from src.env import SCRAPPER_RESULTS_DIR__TELEGRAM

logger = logging.getLogger(__name__)

class InvalidDataException(Exception):
    pass

class TmpListTgPost(BaseModel):
    posts: list[TgPost]

def parse_data(channel_name: str, posts: list[dict[str, str]]) -> list[TgPost]:
    tg_posts: list[TgPost] = []
    try:
        for post in posts:
            tg_posts.append(TgPost(tg_channel_id=post['tg_channel_id'],
                                    tg_post_id=int(post['tg_post_id']),
                                    content=post['content'],
                                    pb_date=datetime.fromisoformat(post['pb_date']),
                                    link=HttpUrl(post['link'])))
    except InvalidDataException as e:
        logger.warning(f'CELERY WORKER :: invalid response data for channel -- {channel_name} -- {e}')
    return tg_posts

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

def _save_to_file(tmp_post, tmp_posts):
    tmp = ""
    if (SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}" / f"{tmp_post.tg_channel_id}__{tmp_post.pb_date.month}.json").exists():
        text = json.load((SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}" / f"{tmp_post.tg_channel_id}__{tmp_post.pb_date.month}.json").open())
        text_posts = text["posts"]
        if isinstance(text_posts, list):
            tmp_posts.insert(0, parse_data(tmp_post.tg_channel_id, text_posts))
            tmp = "TMP"
    (SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}").mkdir(parents=True, exist_ok=True)
    (SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}" / f"{tmp}{tmp_post.tg_channel_id}__{tmp_post.pb_date.month}.json").write_text(
        TmpListTgPost(posts=tmp_posts).model_dump_json(indent=4))
    if tmp == "TMP":
        (SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}" / f"{tmp_post.tg_channel_id}__{tmp_post.pb_date.month}.json").rename(
            (SCRAPPER_RESULTS_DIR__TELEGRAM / tmp_post.tg_channel_id / f"{tmp_post.pb_date.year}" / f"{tmp}{tmp_post.tg_channel_id}__{tmp_post.pb_date.month}.json"))

def save_to_telegram_file(posts: list[TgPost]) -> None:
    heap_sort(posts)
    tmp_posts: list[TgPost] = []
    for post in posts:
        try:
            tmp_post = tmp_posts[-1]
        except IndexError:
            tmp_posts.append(post)
            continue
        if tmp_post.pb_date.month == post.pb_date.month:
            tmp_posts.append(post)
            continue
        else:
            # save
            _save_to_file(tmp_post, tmp_posts)
            tmp_posts.clear()
            tmp_posts.append(post)
    try:
        _save_to_file(tmp_posts[-1], tmp_posts)
    except IndexError:
        pass




@app.task(bind=True)
def parse_api(self, channel_name, task) -> None:
    with httpx.Client() as client:
        response = client.post(f"http://localhost:50001/start", data=task, timeout=10000)
        logger.debug(response.status_code)
        if response.status_code != 200:
            return
    text = response.json()
    if not isinstance(text, list):
        logger.debug(f"noooooooooooooooooooooooooooooooooooo -- {text}")
        return
    tg_posts = parse_data(channel_name, text)
    db = run_on_loop(get_db_main())
    posts = run_on_loop(tg_post_crud.create_tg_posts(db, tg_posts))
    save_to_telegram_file(posts)




