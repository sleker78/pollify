from fastspine import BaseService
from fastspine.cache.cache_decorater import cache_method_async

from app.db.models import Poll, PollOption
from app.db.sessions import PollRepositoryManager
from app.repositories.poll_option_repository import PollOptionRepository
from app.repositories.poll_repository import PollRepository
from app.settings import settings


class PollNotFoundError(Exception):
    pass


class OptionNotFoundError(Exception):
    pass


class PollService(BaseService):
    def __init__(self, db: PollRepositoryManager):
        self.db = db

    async def create_poll(self, question: str, options: list[str]) -> Poll:
        poll = await self.db.get(PollRepository).create(Poll(question=question), commit=False)
        for text in options:
            await self.db.get(PollOptionRepository).create(
                PollOption(poll_id=poll.id, text=text), commit=False
            )
        await self.db.commit()
        return await self._get_poll_or_raise(poll.id)

    async def list_polls(self) -> list[Poll]:
        return await self.db.get(PollRepository).filter_by()

    @cache_method_async(expire=settings.POLL_RESULTS_CACHE_SECONDS, key_prefix="poll")
    async def get_poll_results(self, poll_id: int) -> Poll:
        return await self._get_poll_or_raise(poll_id)

    async def vote(self, poll_id: int, option_id: int) -> None:
        poll = await self._get_poll_or_raise(poll_id)
        if option_id not in {option.id for option in poll.options}:
            raise OptionNotFoundError(f"Option {option_id} does not belong to poll {poll_id}")

        await self.db.get(PollOptionRepository).increment_vote(option_id)

    async def delete_poll(self, poll_id: int) -> None:
        poll = await self._get_poll_or_raise(poll_id)
        await self.db.get(PollRepository).delete(poll, commit=True)

    async def _get_poll_or_raise(self, poll_id: int) -> Poll:
        poll = await self.db.get(PollRepository).get_by_id(poll_id)
        if poll is None:
            raise PollNotFoundError(f"Poll {poll_id} not found")
        return poll
