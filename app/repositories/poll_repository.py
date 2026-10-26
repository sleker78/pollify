from fastspine import BaseRepository

from app.db.models import Poll


class PollRepository(BaseRepository[Poll]):
    """Repository for `Poll` rows."""
