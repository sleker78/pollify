from sqlalchemy import update

from fastspine import BaseRepository

from app.db.models import PollOption


class PollOptionRepository(BaseRepository[PollOption]):
    """Repository for `PollOption` rows."""

    async def increment_vote(self, option_id: int, commit: bool = True) -> None:
        """Atomically increment an option's vote count by one."""
        await self.db.execute(
            update(self.model).where(self.model.id == option_id).values(vote_count=self.model.vote_count + 1)
        )
        if commit:
            await self.commit()
