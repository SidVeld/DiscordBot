FROM ghcr.io/owl-corp/python-poetry-base:3.11-slim

WORKDIR /bot

COPY poetry.lock pyproject.toml ./

RUN poetry install --without dev

COPY . .

CMD ["poetry", "run", "python", "-m", "bot"]

