FROM python:3.10-slim

RUN pip install poetry

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-dev

COPY . .

# TODO: make it so that you don't need to rebuild for config changes

CMD poetry run python -m floodgate

