from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

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
def create_expense(
    expense: ExpenseCreate,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
    current: UserModel = Depends(get_current_user),
) -> ExpenseRead:
    """Create a new expense and persist it."""
    gid = expense.group_id
    pid = expense.payer_id

    group = group_repo.get(gid)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not user_repo.get(pid):
        raise HTTPException(status_code=404, detail="Payer not found")

    member_ids = group.members
    if pid not in member_ids:
        raise HTTPException(
            status_code=400, detail="Payer is not a member of the group"
        )

    e = Expense(
        group_id=gid,
        payer_id=pid,
        amount=int(expense.amount * 100),
        description=expense.description,
    )
    expense_created = repo.add(e)

    return expense_created


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> list[ExpenseRead]:
    return repo.list_all()


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: str,
    repo: SQLAlchemyExpenseRepository = Depends(get_expense_repo),
) -> ExpenseRead:
    try:
        eid = UUID(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    exp = repo.get(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    return exp
