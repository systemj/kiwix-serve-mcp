FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app
COPY . /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

# Default endpoint
ENV KIWIX_SERVER=https://kiwix.lab.systemj.net

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "main.py"]
