from collections import defaultdict
from typing import Dict, Iterable

from .models import Expense


def summarize_balances(expenses: Iterable[Expense]) -> Dict[str, float]:
    """Summarize balances owed per user.

    This simplistic implementation splits each expense equally among group
    members and returns the net amount owed per payer.
    """
    balances: Dict[str, float] = defaultdict(float)
    for expense in expenses:
        shares = expense.amount / 1  # placeholder for number of members
        balances[str(expense.payer_id)] += expense.amount - shares
    return balances
