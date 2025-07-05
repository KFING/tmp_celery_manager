from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class RedisTask(Enum):
    channel_name='channel_name',
    counter_of_workers='cow'

class TelegramTask(BaseModel):
    channel_name: str
    dt_to: datetime
    dt_from: datetime
