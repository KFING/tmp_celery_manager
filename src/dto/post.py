from datetime import datetime, timedelta
from enum import Enum, StrEnum, unique
from pathlib import Path

from pydantic import BaseModel, HttpUrl


class Post(BaseModel):
    channel_name: str
    post_id: int
    content: str
    pb_date: datetime
    link: HttpUrl
    media: dict[str, str] | None

@unique
class Source(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
