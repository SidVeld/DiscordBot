FROM python:3.11-slim as builder

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN python -m pip install pipx
RUN pipx install poetry
RUN pipx run poetry config virtualenvs.in-project true
RUN pipx run poetry install --without dev

COPY /bot ./bot
CMD [ "pipx", "run", "poetry", "run", "python", "-m", "bot" ]
