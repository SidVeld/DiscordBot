from rich.console import Console

from .utils import setup_logger, get_version, get_quote


VERSION = get_version()
QUOTE = get_quote()

console = Console()
console.print(f"INCARN {VERSION}", style="yellow", highlight=False)
console.print(QUOTE, style="red")
console.print()

setup_logger()
