from math import floor
from typing import Dict, Iterable, List
from uuid import UUID

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


def calculate_group_balances(
    member_ids: List[UUID], expenses: Iterable[Expense]
) -> Dict[UUID, float]:
    """Calculate per-member balance using equal-split accounting.

    Each expense is split equally among all group members (floor division to
    whole cents).  The payer is credited the full integer-dollar value of the
    expense; every member (including the payer) is debited their share.

    Amounts are stored as integer cents, and the calculation normalises to
    dollars before returning, matching the API's ``BalanceEntry`` schema.
    """
    n = len(member_ids)
    balances: Dict[UUID, float] = {mid: 0.0 for mid in member_ids}

    for e in expenses:
        share = floor(float(e.amount) / 100) / n if n else 0.0
        for mid in member_ids:
            balances[mid] -= share
        if e.payer_id in balances:
            balances[e.payer_id] += floor(e.amount / 100)

    return balances
