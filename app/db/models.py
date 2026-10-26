from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastspine.mixins import CreatedAtMixin
from fastspine.models.base import Base


class Poll(Base, CreatedAtMixin):
    __tablename__ = "polls"

    question: Mapped[str]

    options: Mapped[list["PollOption"]] = relationship(
        back_populates="poll", lazy="selectin", cascade="all, delete-orphan"
    )


class PollOption(Base):
    __tablename__ = "poll_options"

    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id", ondelete="CASCADE"))
    text: Mapped[str]
    vote_count: Mapped[int] = mapped_column(default=0)

    poll: Mapped[Poll] = relationship(back_populates="options")
