import random
from pathlib import Path

from tomllib import load

PYPROJECT_PATH = Path("pyproject.toml")


def get_version() -> str:
    pyproject_data = load(PYPROJECT_PATH.open("rb"))
    return pyproject_data["tool"]["poetry"]["version"]


def get_quote() -> str:
    quotes = [
        "Young and stupid.",
        "From dirt to dukes.",
        "I love you, I hate you."
    ]
    return random.choice(quotes)
