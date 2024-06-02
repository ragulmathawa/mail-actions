.PHONY: all
.DEFAULT_GOAL:= help
run: ## Run
	poetry run python mail_actions.py
fmt: ## Format
	poetry run python -m black .
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'