"""Pollify CLI - the same PollService the API uses, called from the terminal instead of HTTP."""

from typing import Annotated

import typer

import app.bootstrap  # noqa: F401  (must run before any command uses PollRepositoryManager)

from fastspine import load_service
from fastspine.cli.scoped_typer import ScopedTyper

from app.services.poll_service import OptionNotFoundError, PollNotFoundError, PollService

app = ScopedTyper(no_args_is_help=True, help="Manage Pollify polls from the terminal.")


@app.command("create", help="Create a poll with two or more options.")
async def create_poll(
    question: str,
    option: Annotated[list[str], typer.Option("--option", "-o", help="Repeat for each option.")],
):
    if len(option) < 2:
        typer.echo("A poll needs at least 2 options.", err=True)
        raise typer.Exit(code=1)

    service = load_service(PollService)
    poll = await service.create_poll(question, option)
    typer.echo(f"Created poll #{poll.id}: {poll.question}")
    for opt in poll.options:
        typer.echo(f"  [{opt.id}] {opt.text}")


@app.command("list", help="List all polls.")
async def list_polls():
    service = load_service(PollService)
    polls = await service.list_polls()
    if not polls:
        typer.echo("No polls yet - create one with `create`.")
        return
    for poll in polls:
        typer.echo(f"[{poll.id}] {poll.question}")


@app.command("results", help="Show a poll's options and vote counts.")
async def results(poll_id: int):
    service = load_service(PollService)
    try:
        poll = await service.get_poll_results(poll_id)
    except PollNotFoundError as err:
        typer.echo(str(err), err=True)
        raise typer.Exit(code=1) from err

    typer.echo(poll.question)
    for opt in poll.options:
        typer.echo(f"  {opt.text}: {opt.vote_count}")


@app.command("vote", help="Vote for an option.")
async def vote(poll_id: int, option_id: int):
    service = load_service(PollService)
    try:
        await service.vote(poll_id, option_id)
    except (PollNotFoundError, OptionNotFoundError) as err:
        typer.echo(str(err), err=True)
        raise typer.Exit(code=1) from err
    typer.echo("Vote recorded.")


if __name__ == "__main__":
    app()
