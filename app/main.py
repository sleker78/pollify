from contextlib import asynccontextmanager
from typing import Annotated

import app.bootstrap  # noqa: F401  (must run before any route uses PollRepositoryManager)

from fastapi import Depends, FastAPI, HTTPException

from fastspine import FastSpineApp, service_dep
from fastspine.models.base import Base

from app.services.poll_service import OptionNotFoundError, PollNotFoundError, PollService
from app.schemas import PollCreateRequest, PollResponse, PollSummaryResponse, VoteRequest
from app.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = settings.db_config.create_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield


app = FastSpineApp(settings=settings, lifespan=lifespan)

PollServiceDep = Annotated[PollService, Depends(service_dep(PollService))]


@app.post("/polls", response_model=PollResponse)
async def create_poll(payload: PollCreateRequest, service: PollServiceDep):
    poll = await service.create_poll(payload.question, payload.options)
    return PollResponse.from_model(poll)


@app.get("/polls", response_model=list[PollSummaryResponse])
async def list_polls(service: PollServiceDep):
    polls = await service.list_polls()
    return [PollSummaryResponse.model_validate(poll) for poll in polls]


@app.get("/polls/{poll_id}", response_model=PollResponse)
async def get_poll(poll_id: int, service: PollServiceDep):
    try:
        poll = await service.get_poll_results(poll_id)
    except PollNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return PollResponse.from_model(poll)


@app.post("/polls/{poll_id}/vote", status_code=204)
async def vote(poll_id: int, payload: VoteRequest, service: PollServiceDep):
    try:
        await service.vote(poll_id, payload.option_id)
    except PollNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except OptionNotFoundError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.delete("/polls/{poll_id}", status_code=204)
async def delete_poll(poll_id: int, service: PollServiceDep):
    try:
        await service.delete_poll(poll_id)
    except PollNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
