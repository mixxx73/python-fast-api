"""Group routes: create, list, retrieve, update groups and manage balances."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..domain.exceptions import GroupNotFoundError, UserNotFoundError
from ..domain.models import Group
from ..domain.models import User as UserModel
from ..domain.services import calculate_group_balances
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
async def create_group(
    group: GroupCreate,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    _current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Create a new group and persist it."""
    new_group = Group(name=group.name)
    await group_repo.add(new_group)
    return GroupRead(id=new_group.id, name=new_group.name, members=new_group.members)


@router.post("/{group_id}/members/{user_id}", response_model=GroupRead)
async def add_member(
    group_id: UUID,
    user_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    _current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Add a user to a group and return the updated group."""
    if not await user_repo.get(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not await group_repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    await group_repo.add_member(group_id, user_id)
    for g in await group_repo.list_for_user(user_id):
        if g.id == group_id:
            return GroupRead(id=g.id, name=g.name, members=g.members)

    return GroupRead(id=group_id, name="", members=[user_id])


@router.get("/{group_id}/expenses", response_model=list[ExpenseRead])
async def list_group_expenses(
    group_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    expense_repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> list[ExpenseRead]:
    """List expenses for a group."""
    if not await group_repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    expenses = await expense_repo.list_for_group(group_id)
    return [
        ExpenseRead(
            id=e.id,
            group_id=e.group_id,
            payer_id=e.payer_id,
            amount=e.amount,
            created_at=e.created_at,
            description=e.description,
        )
        for e in expenses
    ]


@router.get("/", response_model=list[GroupRead])
async def list_groups(
    repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user: UserModel = Depends(get_current_user),
) -> list[GroupRead]:
    """List all groups (admin) or just the current user's groups."""
    groups = await repo.list_all() if user.is_admin else await repo.list_for_user(user.id)
    return [GroupRead(id=g.id, name=g.name, members=g.members) for g in groups]


@router.get("/{group_id}", response_model=GroupRead)
async def get_group(
    group_id: UUID,
    repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
) -> GroupRead:
    """Return a single group by UUID."""
    group = await repo.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupRead(id=group.id, name=group.name, members=group.members)


@router.patch("/{group_id}", response_model=GroupRead)
async def update_group(
    group_id: UUID,
    payload: GroupUpdate,
    repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    _current: UserModel = Depends(get_current_user),
) -> GroupRead:
    """Rename a group."""
    if not await repo.get(group_id):
        raise HTTPException(status_code=404, detail="Group not found")

    await repo.update_name(group_id, payload.name)
    updated = await repo.get(group_id)

    if updated is None:
        logger.error(
            f"Failed to update group {group_id}.",
            exc_info=True,
            extra={"group_id": str(group_id)},
        )
        raise HTTPException(status_code=422, detail="Failed to update profile")

    return GroupRead(id=updated.id, name=updated.name, members=updated.members)


@router.get("/{group_id}/balances", response_model=list[BalanceEntry])
async def get_group_balances(
    group_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    expense_repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> list[BalanceEntry]:
    """Retrieve balance information for a group."""
    group = await group_repo.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if not group.members:
        return []

    expenses = await expense_repo.list_for_group(group_id)
    balances = calculate_group_balances(group.members, expenses)

    return [{"user_id": uid, "balance": round(bal, 2)} for uid, bal in balances.items()]
