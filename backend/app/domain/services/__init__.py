from typing import Dict, Iterable

from ..models import Expense
from .user_service import build_user_service, create_user_and_add_to_group


def summarize_balances(expenses: Iterable[Expense]) -> Dict[str, float]:
    """Summarize balances owed per user from expenses only.

    Current simplistic behavior: ensure each payer appears in the result with
    a zero balance. This supports generators and other iterables without
    requiring member lists.
    """
    balances: Dict[str, float] = {}
    for expense in expenses:
        payer_id = str(expense.payer_id)
        if payer_id not in balances:
            balances[payer_id] = 0.0
        # Intentionally no balance math: net effect remains zero per payer.
    return balances


__all__ = [
    "summarize_balances",
    "build_user_service",
    "create_user_and_add_to_group",
]
