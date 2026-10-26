from pydantic_settings import BaseSettings

from fastspine.database.engine import DBConfig, DBServices


class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Pollify"
    DEBUG_MODE: bool = False

    DB_NAME: str = "pollify"
    DB_USER: str = "pollify"
    DB_PASSWORD: str = "pollify"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    CACHE_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""
    REDIS_PASSWORD: str = ""
    CACHED_DISABLED_USERS: list[str] = []

    # Celery isn't used by this app, but CoreSettings requires every non-Optional field
    # from every settings group regardless of which features are actually in use.
    CELERY_RESULT_EXPIRES: int = 7 * 24 * 60 * 60
    CELERY_BROKER_URI: str = ""
    CELERY_BACKEND_URI: str = "redis://localhost:6385/0"
    CELERY_MAIN_NAME: str = "_redis_main"
    CELERY_TASK_FOLDERS: list[str] = []
    WORKERS_ON: bool = False
    VISIBILITY_TIMEOUT: int = 3600

    PROFILER_LOG_LEVEL: int = 20  # logging.INFO

    POLL_RESULTS_CACHE_SECONDS: int = 20

    @property
    def db_config(self) -> DBConfig:
        return DBConfig(
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            service=DBServices.ASYNC_POSTGRES,
        )


settings = AppSettings()
