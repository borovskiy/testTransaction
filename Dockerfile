FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first (layer caching)
COPY pyproject.toml poetry.lock /app/

# Install dependencies globally (not in venv)
RUN poetry install --no-root

# Copy all project files
COPY . /app/

CMD ["bash"]
