FROM python:3.11-slim as builder

WORKDIR /incarn

COPY poetry.lock pyproject.toml ./

RUN pip install poetry --no-cache-dir \
    && poetry config virtualenvs.in-project true \
    && poetry install --without dev

COPY bot/ ./bot/

CMD ["poetry", "run", "python", "-m", "bot"]
