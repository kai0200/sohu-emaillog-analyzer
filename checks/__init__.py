"""
Check registry and helpers for log analysis.
"""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Tuple

from .helo_error import run as check_helo_error
from .no_related import run as check_no_related
from .sent_250 import run as check_250_success
from .spf_error import run as check_spf_error

CheckFunc = Callable[[str, str, str], bool]
CheckEntry = Tuple[str, CheckFunc]

# Execution order matters – earlier checks have higher priority.
CHECKS: List[CheckEntry] = [
    ("spf_error", check_spf_error),
    ("helo_error", check_helo_error),
    ("no_related", check_no_related),
    ("sent_250", check_250_success),
]


def run_checks(text: str, sender: str, recipient: str, checks: Optional[Iterable[CheckEntry]] = None) -> str:
    """
    Run the configured checks sequentially until one of them handles the log.

    Args:
        text: Combined log text.
        sender: Sender address (or domain prefixed with "@").
        recipient: Recipient address.
        checks: Optional override list of check entries, mainly for testing.

    Returns:
        The name of the first check that handled the log; an empty string
        indicates no check claimed the log.
    """

    for name, func in checks or CHECKS:
        if func(text, sender, recipient):
            return name
    return ""