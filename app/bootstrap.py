from fastspine.dependencies.database import register_sessions
from fastspine.settings import init_core_settings

from app.db.sessions import PollRepositoryManager
from app.settings import settings

# FastSpineApp does this for the API process automatically; the CLI process has no
# equivalent hook, so it's done here once, covering both entrypoints that import this module.
init_core_settings(settings=settings)

register_sessions([
    (PollRepositoryManager, settings.db_config),
])
