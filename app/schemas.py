from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import Poll


class PollCreateRequest(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)


class VoteRequest(BaseModel):
    option_id: int


class PollOptionResponse(BaseModel):
    id: int
    text: str
    vote_count: int

    model_config = {"from_attributes": True}


class PollResponse(BaseModel):
    id: int
    question: str
    created_at: datetime
    options: list[PollOptionResponse]

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, poll: Poll) -> "PollResponse":
        return cls.model_validate(poll)


class PollSummaryResponse(BaseModel):
    id: int
    question: str

    model_config = {"from_attributes": True}
