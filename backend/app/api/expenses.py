"""Expense routes: create, list, and retrieve individual expenses."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..domain.exceptions import ExpenseCreateError
from ..domain.models import Expense
from ..domain.models import User as UserModel
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
from .schemas import ExpenseCreate, ExpenseRead

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseRead)
async def create_expense(
    expense: ExpenseCreate,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
    _current: UserModel = Depends(get_current_user),
) -> ExpenseRead:
    """Create a new expense and persist it."""
    gid = expense.group_id
    pid = expense.payer_id

    group = await group_repo.get(gid)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not await user_repo.get(pid):
        raise HTTPException(status_code=404, detail="Payer not found")

    if pid not in group.members:
        raise HTTPException(
            status_code=400, detail="Payer is not a member of the group"
        )

    e = Expense(
        group_id=gid,
        payer_id=pid,
        amount=int(expense.amount * 100),
        description=expense.description,
    )

    try:
        expense_created = await repo.add(e)
    except ExpenseCreateError as exc:
        raise HTTPException(status_code=400, detail="Failed to create expense") from exc

    return expense_created


@router.get("/", response_model=list[ExpenseRead])
async def list_expenses(
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> list[ExpenseRead]:
    """Return all expenses."""
    return await repo.list_all()


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: str,
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> ExpenseRead:
    """Return a single expense by UUID."""
    try:
        eid = UUID(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    exp = await repo.get(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp
