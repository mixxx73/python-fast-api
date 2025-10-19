from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..domain.models import Group
from ..domain.models import User as UserModel
from ..infrastructure.database import get_db
from ..infrastructure.orm import ExpenseORM, GroupORM
from ..infrastructure.repositories import (
    SQLAlchemyExpenseRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import BalanceEntry, ExpenseRead, GroupCreate, GroupRead, GroupUpdate

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupRead)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Create a new group and persist it."""
    repo = SQLAlchemyGroupRepository(db)
    domain_group = Group(name=group.name)
    repo.add(domain_group)
    # The domain_group object is updated with the ID after the commit.
    return GroupRead.from_orm(domain_group)


@router.post("/{group_id}/members/{user_id}", response_model=GroupRead)
def add_member(
    group_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Add a user to a group and return the updated group."""
    group_repo = SQLAlchemyGroupRepository(db)
    user_repo = SQLAlchemyUserRepository(db)

    # FastAPI handles UUID validation. The existence checks are still needed.
    if not user_repo.get(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    group = group_repo.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group_repo.add_member(group_id, user_id)

    # Re-fetch the group to get the updated member list.
    updated_group = group_repo.get(group_id)
    if not updated_group:
        # This should not happen if the group existed before.
        raise HTTPException(status_code=500, detail="Failed to retrieve group after update")

    return GroupRead.from_orm(updated_group)


@router.get("/{group_id}/expenses", response_model=list[ExpenseRead])
def list_group_expenses(
    group_id: UUID, db: Session = Depends(get_db)
) -> list[ExpenseRead]:
    """List expenses for a group."""
    group_repo = SQLAlchemyGroupRepository(db)
    if not group_repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    expense_repo = SQLAlchemyExpenseRepository(db)
    expenses = expense_repo.list_for_group(group_id)
    return [ExpenseRead.from_orm(e) for e in expenses]


@router.get("/", response_model=list[GroupRead])
def list_groups(db: Session = Depends(get_db)) -> list[GroupRead]:
    repo = SQLAlchemyGroupRepository(db)
    groups = repo.list_all()
    return [GroupRead.from_orm(g) for g in groups]


@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: UUID, db: Session = Depends(get_db)) -> GroupRead:
    repo = SQLAlchemyGroupRepository(db)
    group = repo.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupRead.from_orm(group)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(
    group_id: UUID,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    current: UserModel = Depends(get_current_user),
) -> GroupRead:
    repo = SQLAlchemyGroupRepository(db)
    if not repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    repo.update_name(group_id, payload.name)
    updated = repo.get(group_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to retrieve group after update")

    return GroupRead.from_orm(updated)


@router.get("/{group_id}/balances", response_model=list[BalanceEntry])
def get_group_balances(group_id: UUID, db: Session = Depends(get_db)) -> list[BalanceEntry]:
    # Note: This endpoint contains significant business logic for calculating balances.
    # In a larger application, this logic should be moved to a dedicated service or
    # domain layer to keep the API endpoint thin and focused on HTTP handling.
    # It also bypasses the repository pattern by directly using the ORM.

    try:
        group = db.get(GroupORM, group_id)
    except Exception:
        # Note: Broadly catching exceptions like this is risky as it can hide
        # underlying issues. The original comment mentioned driver-specific type
        # coercion errors, which should ideally be addressed at the source.
        return []

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = [m.id for m in group.members]
    if not members:
        return []

    balances = {mid: 0.0 for mid in members}
    expenses = db.query(ExpenseORM).filter(ExpenseORM.group_id == group_id).all()
    n = len(members)

    for e in expenses:
        share = float(e.amount) / n if n > 0 else 0.0
        for mid in members:
            balances[mid] -= share
        if e.payer_id in balances:
            balances[e.payer_id] += float(e.amount)

    return [
        BalanceEntry(user_id=uid, balance=round(bal, 2))
        for uid, bal in balances.items()
    ]
