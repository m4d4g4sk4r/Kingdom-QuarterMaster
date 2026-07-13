"""Pre-rendered ASCII/ANSI branding banner shown on `kqm --help` / `kqm -h`.

The wordmark is embedded as a constant (rendered once at design time with
pyfiglet's ``ansi_shadow`` font). The base CLI therefore needs no figlet or
image dependency at runtime — only ``rich``, which the CLI already uses.
Colour is applied via rich and is stripped automatically when stdout is not a
terminal (e.g. piped to a file), leaving clean ASCII.
"""

from __future__ import annotations

from rich.console import Console

# Kingdom Corporation amber (matches the web UI accent — see DESIGN_BRIEF.md).
AMBER = "#e6a23c"

# "KINGDOM" — pyfiglet ansi_shadow, embedded verbatim. 58 columns wide.
_WORDMARK = r"""
██╗  ██╗██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ███╗   ███╗
██║ ██╔╝██║████╗  ██║██╔════╝ ██╔══██╗██╔═══██╗████╗ ████║
█████╔╝ ██║██╔██╗ ██║██║  ███╗██║  ██║██║   ██║██╔████╔██║
██╔═██╗ ██║██║╚██╗██║██║   ██║██║  ██║██║   ██║██║╚██╔╝██║
██║  ██╗██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝
"""

_RULE = "─" * 58
_SUBTITLE = "Q U A R T E R M A S T E R   ·   read-only requisition terminal"


def render_banner(console: Console | None = None) -> None:
    """Print the branding banner (wordmark + subtitle) to ``console``."""
    console = console or Console()
    console.print(_WORDMARK.strip("\n"), style=f"bold {AMBER}", highlight=False)
    console.print(f"[{AMBER}]{_RULE}[/]", highlight=False)
    console.print(f"[dim]{_SUBTITLE}[/dim]\n", highlight=False)
