clean:
	find . | grep -E "(__pycache__$|\.pyc$|\.pyo$|.idea$|.ruff_cache$)" | xargs rm -rf

dev:
	docker compose up --build --remove-orphans

run:
	uv run fastapi dev

format:
	uv run ruff format

lint:
	uv run ruff check --fix

push: format lint

# CI

NAME = upa-ux-api
VERSION = latest
REGISTRY = 
TAG = $(NAME):$(VERSION)

ci-build:
	docker build -t $(TAG) .
	docker tag $(TAG) $(REGISTRY)/$(TAG)

ci-push:
	docker push $(REGISTRY)/$(TAG)

ci-deploy: ci-build ci-push
