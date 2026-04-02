from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Expense
from ..domain.models import User as UserModel
from ..infrastructure.database import get_db
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
    db: AsyncSession = Depends(get_db),
    _current: UserModel = Depends(get_current_user),
) -> ExpenseRead:
    """Create a new expense and persist it."""
    group_repo = SQLAlchemyGroupRepository(db)
    user_repo = SQLAlchemyUserRepository(db)

    gid = expense.group_id
    pid = expense.payer_id

    group = await group_repo.get(gid)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not await user_repo.get(pid):
        raise HTTPException(status_code=404, detail="Payer not found")

    if pid not in group.members:
        raise HTTPException(status_code=400, detail="Payer is not a member of the group")

    repo = SQLAlchemyExpenseRepository(db)
    e = Expense(
        group_id=gid,
        payer_id=pid,
        amount=int(expense.amount * 100),
        description=expense.description,
    )
    expense_created = await repo.add(e)
    return expense_created


@router.get("/", response_model=list[ExpenseRead])
async def list_expenses(db: AsyncSession = Depends(get_db)) -> list[ExpenseRead]:
    repo = SQLAlchemyExpenseRepository(db)
    return await repo.list_all()


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(expense_id: str, db: AsyncSession = Depends(get_db)) -> ExpenseRead:
    try:
        eid = UUID(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    repo = SQLAlchemyExpenseRepository(db)
    exp = await repo.get(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp
