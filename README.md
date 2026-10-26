# Pollify

A tiny polling API - create a poll, vote on it, see live-ish results. Built on
[FastSpine](https://github.com/sleker78/fastspine) to demonstrate its service-repository pattern,
async Postgres, and Redis caching in a small, real app.

## Run it

```bash
make up
```

(or plain `docker compose up --build -d` if you don't have `make`). Then open
**http://localhost:8000/docs** - FastAPI's Swagger UI lets you try every endpoint directly in the
browser, no separate frontend needed.

Other commands: `make logs` (follow app logs), `make restart` (rebuild just the app),
`make reset` (wipe the database and start fresh), `make down` (stop everything).

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `POST` | `/polls` | Create a poll with 2+ options |
| `GET` | `/polls` | List all polls |
| `GET` | `/polls/{id}` | Get a poll with its options and vote counts - **cached** for 20s |
| `POST` | `/polls/{id}/vote` | Vote for one of the poll's options |
| `DELETE` | `/polls/{id}` | Delete a poll |

## Try it

```bash
# create a poll
curl -X POST localhost:8000/polls -H "Content-Type: application/json" \
  -d '{"question": "Best editor?", "options": ["vim", "emacs", "vscode"]}'

# vote (option_id from the response above)
curl -X POST localhost:8000/polls/1/vote -H "Content-Type: application/json" \
  -d '{"option_id": 1}'

# see results - cached for 20s, so repeated votes within that window
# won't show up immediately in the count
curl localhost:8000/polls/1
```

## CLI

The same `PollService` the API uses, callable from the terminal too - via FastSpine's
`ScopedTyper` ([docs](https://github.com/sleker78/fastspine/blob/main/_docs/cli.md)):

```bash
make cli ARGS="create \"Best editor?\" -o vim -o emacs -o vscode"
make cli ARGS="list"
make cli ARGS="results 1"
make cli ARGS="vote 1 1"
```

(or, without Docker: `uv run python -m app.cli.main <command>`.) Each invocation opens and closes
its own DB session around the command - no FastAPI request involved, same `PollService` code path.

## Why the results are "live-ish", not live

`GET /polls/{id}` is cached with a short TTL (`POLL_RESULTS_CACHE_SECONDS`, default 20s) via
FastSpine's `cache_method_async`. Voting doesn't invalidate the cache - results become eventually
consistent for up to the TTL window. That's intentional: it's the simple, honest version of
caching something that changes, instead of wiring up manual cache-busting on every vote.

## Architecture

- `app/db/models.py` - `Poll`/`PollOption` SQLAlchemy models
- `app/db/sessions.py` + `app/bootstrap.py` - the one `RepositoryManager` and its registration
- `app/repositories/` - `PollRepository`, `PollOptionRepository` (atomic vote increment)
- `app/services/poll_service.py` - business logic: a vote must target an option that actually
  belongs to the poll being voted on; caching the results read
- `app/main.py` - the 5 FastAPI routes, each just calling one `PollService` method
- `app/cli/main.py` - a `ScopedTyper` CLI calling the exact same `PollService` methods

See FastSpine's own docs for the underlying patterns:
[Database](https://github.com/sleker78/fastspine/blob/main/_docs/database.md),
[Caching](https://github.com/sleker78/fastspine/blob/main/_docs/caching.md).

## Local dev without Docker

Needs a local Postgres and Redis reachable at the hosts/ports in `app/settings.py` (defaults to
`localhost`):

```bash
uv sync
uv run uvicorn app.main:app --reload
```
