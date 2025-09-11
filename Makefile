.PHONY: lint

lint:
	@docker compose --profile dev run --rm lint

.PHONY: lint-fix

lint-fix:
	@docker compose --profile dev run --rm lint-fix

.PHONY: frontend-lint

frontend-lint:
	@docker compose --profile dev run --rm frontend-lint

.PHONY: frontend-lint-fix

frontend-lint-fix:
	@docker compose --profile dev run --rm frontend-lint-fix

.PHONY: lint-all

lint-all:
	@docker compose --profile dev run --rm lint && \
	 docker compose --profile dev run --rm frontend-lint

.PHONY: lint-fix-all

lint-fix-all:
	@docker compose --profile dev run --rm lint-fix && \
	 docker compose --profile dev run --rm frontend-lint-fix

.PHONY: frontend-test

frontend-test:
	@docker compose --profile test run --rm frontend-tests

.PHONY: install-hooks

install-hooks:
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit
	@echo "Git hooks installed (core.hooksPath=.githooks)"
