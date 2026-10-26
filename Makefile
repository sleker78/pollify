.PHONY: up
up:  ## Build and start the full stack (app + Postgres + Redis) in the background
	docker compose up --build -d

.PHONY: down
down:  ## Stop the stack
	docker compose down

.PHONY: reset
reset:  ## Stop the stack and wipe the Postgres volume (fresh database on next up)
	docker compose down -v

.PHONY: logs
logs:  ## Follow app logs
	docker compose logs -f app

.PHONY: restart
restart:  ## Rebuild and restart just the app container
	docker compose up --build -d app

.PHONY: ps
ps:  ## Show container status
	docker compose ps

.PHONY: cli
cli:  ## Run a Pollify CLI command inside the app container, e.g. make cli ARGS="list"
	docker compose exec app python -m app.cli.main $(ARGS)
