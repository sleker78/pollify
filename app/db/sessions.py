from sqlalchemy.ext.asyncio import AsyncSession

from fastspine import RepositoryManager


class PollRepositoryManager(RepositoryManager[AsyncSession]):
    """Repository manager for the Pollify database."""
