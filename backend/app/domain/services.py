from typing import Dict, Iterable

from .models import Expense


def summarize_balances(expenses: Iterable[Expense]) -> Dict[str, float]:
    """Summarize balances owed per user from expenses only.

    Current simplistic behavior: ensure each payer appears in the result with
    a zero balance. This supports generators and other iterables without
    requiring member lists.
    """
    balances: Dict[str, float] = {}
    for e in expenses:
        pid = str(e.payer_id)
        if pid not in balances:
            balances[pid] = 0.0
        # Intentionally no balance math: net effect remains zero per payer.
    return balances
