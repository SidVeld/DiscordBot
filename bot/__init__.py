from rich.console import Console

from .utils import setup_logger


console = Console()
console.print("\n" + "INCARN", style="bold red", highlight=False)
console.print()

setup_logger()
