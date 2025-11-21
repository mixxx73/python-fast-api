import logging
from math import floor
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DataError, StatementError
from sqlalchemy.orm import Session

from ..domain.models import Group
from ..domain.models import User as UserModel
from ..infrastructure.database import get_db
from ..infrastructure.dependencies import (
    get_expense_repo,
    get_group_repo,
    get_user_repo,
)
from ..infrastructure.repositories import (
    SQLAlchemyExpenseRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import BalanceEntry, ExpenseRead, GroupCreate, GroupRead, GroupUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupRead)
def create_group(
    group: GroupCreate,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Create a new group and persist it."""

    group = Group(name=group.name)
    group_repo.add(group)

    return GroupRead(id=group.id, name=group.name, members=group.members)


@router.post("/{group_id}/members/{user_id}", response_model=GroupRead)
def add_member(
    group_id: UUID,
    user_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Add a user to a group and return the updated group."""
    if not user_repo.get(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not group_repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    group_repo.add_member(group_id, user_id)
    for g in group_repo.list_for_user(user_id):
        if g.id == group_id:
            return GroupRead(id=g.id, name=g.name, members=g.members)

    return GroupRead(id=group_id, name="", members=[user_id])


@router.get("/{group_id}/expenses", response_model=list[ExpenseRead])
def list_group_expenses(
    group_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    expense_repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> list[ExpenseRead]:
    """List expenses for a group."""
    if not group_repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    from datetime import datetime, timezone

    def as_dt(v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc)
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                pass
        return datetime.now(timezone.utc)

    return [
        ExpenseRead(
            id=e.id,
            group_id=e.group_id,
            payer_id=e.payer_id,
            amount=e.amount,
            created_at=as_dt(e.created_at),
            description=e.description,
        )
        for e in expense_repo.list_for_group(group_id)
    ]


@router.get("/", response_model=list[GroupRead])
def list_groups(
    repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user: UserModel = Depends(get_current_user),
) -> list[GroupRead]:
    groups = repo.list_all() if user.is_admin else repo.list_for_user(user.id)
    return [GroupRead(id=g.id, name=g.name, members=g.members) for g in groups]


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: UUID, repo: SQLAlchemyGroupRepository = Depends(get_group_repo)
) -> GroupRead:
    group = repo.get(group_id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return GroupRead(id=group.id, name=group.name, members=group.members)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(
    group_id: UUID,
    payload: GroupUpdate,
    repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    if not repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    repo.update_name(group_id, payload.name)
    updated = repo.get(group_id)

    if updated is None:
        logger.error(
            f"Failed to update group {group_id}. ",
            exc_info=True,
            extra={"group_id": str(group_id)},
        )
        raise HTTPException(status_code=422, detail="Failed to update profile")

    return GroupRead(id=updated.id, name=updated.name, members=updated.members)


@router.get("/{group_id}/balances", response_model=list[BalanceEntry])
def get_group_balances(
    group_id: UUID, db: Session = Depends(get_db)
) -> list[BalanceEntry]:
    """Retrieve balance information for a group.

    Returns a list of balance entries (user_id, balance) for each member.
    """
    from ..infrastructure.orm import ExpenseORM, GroupORM

    try:
        group = db.get(GroupORM, group_id)
    except (StatementError, DataError) as e:
        logger.error(
            f"Database error while loading group {group_id}: {e}",
            exc_info=True,
            extra={"group_id": str(group_id)},
        )
        raise HTTPException(
            status_code=500, detail="Internal server error loading group data"
        )

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = [m.id for m in group.members]
    if not members:
        return []

    balances = {mid: 0.0 for mid in members}

    expenses = db.query(ExpenseORM).filter(ExpenseORM.group_id == group_id).all()

    n = len(members)
    for e in expenses:
        share = floor(float(e.amount) / 100) / n if n else 0.0
        for mid in members:
            balances[mid] -= share

        if e.payer_id in balances:
            balances[e.payer_id] += floor(e.amount / 100)

    # return balances
    return [
        # BalanceEntry(user_id=uid, balance=round(bal, 2))
        {"user_id": uid, "balance": round(bal, 2)}
        for uid, bal in balances.items()
    ]
