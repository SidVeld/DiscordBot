from rich.console import Console

from .utils import get_quote, get_version, setup_logger

VERSION = get_version()
QUOTE = get_quote()

console = Console()
console.print(f"INCARN {VERSION}", style="yellow", highlight=False)
console.print(QUOTE, style="red")
console.print()

setup_logger()
