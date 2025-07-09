import logging
import os
import pathlib
from enum import Enum, unique
from pathlib import Path
from typing import Final

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings

ROOT_PATH = Path(__file__).parent.parent.parent


ENV_IS_TEST = os.environ.get("ENV", None) == "test"

logger = logging.getLogger(__name__)


@unique
class AppName(Enum):
    app_api = "app_api"
    app_celery = "app_celery"
    app_dash = "app_dash"

    @property
    def app_directory(self) -> pathlib.Path:
        return ROOT_PATH / "src" / self.value


@unique
class AppEnv(Enum):
    CI = "ci"
    TEST = "test"
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    ROOT_PATH: Path = ROOT_PATH
    LOG_LVL: LogLevel = LogLevel.INFO

    SENTRY_DSN: str = ""

    ENV: AppEnv = AppEnv.PROD
    app: AppName  # must be set in constructor

    SECRET_KEY: SecretStr = SecretStr("")

    MAIN_DB_URL: SecretStr = SecretStr("")
    CACHE_DB_URL: SecretStr = SecretStr("")

    CELERY_BACKEND: SecretStr = SecretStr("")
    CELERY_BROKER: SecretStr = SecretStr("")


    @property
    def is_local(self) -> bool:
        return self.ENV == AppEnv.LOCAL

    @property
    def is_testing(self) -> bool:
        return self.ENV in {AppEnv.CI, AppEnv.TEST}

    @property
    def is_prod(self) -> bool:
        return self.ENV == AppEnv.PROD

    class Config:  # pyright: ignore
        env_file = ROOT_PATH / ".env" if not ENV_IS_TEST else ROOT_PATH / ".env.test"


# TODO: replace with right app
settings: Final = Settings(app=AppName.app_api)  # pyright: ignore

SCRAPPER_TMP_MEDIA_DIR = settings.ROOT_PATH / ".tmp" / "media"

SCRAPPER_TMP_MEDIA_DIR__YOUTUBE = settings.ROOT_PATH / ".var" / "data" / "youtube"
SCRAPPER_TMP_MEDIA_DIR__INSTAGRAM = settings.ROOT_PATH / ".var" / "data" / "instagram"
SCRAPPER_TMP_MEDIA_DIR__TELEGRAM = settings.ROOT_PATH / ".var" / "data" / "telegram"

SCRAPPER_RESULTS_DIR = settings.ROOT_PATH / ".var" / "data"
SCRAPPER_RESULTS_DIR__YOUTUBE = settings.ROOT_PATH / ".var" / "data" / "youtube"
SCRAPPER_RESULTS_DIR__INSTAGRAM = settings.ROOT_PATH / ".var" / "data" / "instagram"
SCRAPPER_RESULTS_DIR__TELEGRAM = settings.ROOT_PATH / ".var" / "data" / "telegram"

SCRAPPER_TMP_MEDIA_DIR.mkdir(exist_ok=True, parents=True)
SCRAPPER_TMP_MEDIA_DIR__YOUTUBE.mkdir(exist_ok=True, parents=True)
SCRAPPER_TMP_MEDIA_DIR__INSTAGRAM.mkdir(exist_ok=True, parents=True)
SCRAPPER_TMP_MEDIA_DIR__TELEGRAM.mkdir(exist_ok=True, parents=True)
SCRAPPER_RESULTS_DIR__YOUTUBE.mkdir(exist_ok=True, parents=True)
SCRAPPER_RESULTS_DIR__INSTAGRAM.mkdir(exist_ok=True, parents=True)
SCRAPPER_RESULTS_DIR__TELEGRAM.mkdir(exist_ok=True, parents=True)

