from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current: UserModel = Depends(get_current_user),
) -> ExpenseRead:
    """Create a new expense and persist it."""
    group_repo = SQLAlchemyGroupRepository(db)
    user_repo = SQLAlchemyUserRepository(db)

    gid = expense.group_id
    pid = expense.payer_id

    if not group_repo.get(gid):
        raise HTTPException(status_code=404, detail="Group not found")
    if not user_repo.get(pid):
        raise HTTPException(status_code=404, detail="Payer not found")

    # Note: This is an inefficient way to check for membership.
    # It fetches all groups for a user. A more direct method like
    # `group_repo.is_member(gid, pid)` would be better.
    member_groups = [g.id for g in group_repo.list_for_user(pid)]
    if gid not in member_groups:
        raise HTTPException(
            status_code=400, detail="Payer is not a member of the group"
        )

    repo = SQLAlchemyExpenseRepository(db)
    domain_expense = Expense(
        group_id=gid,
        payer_id=pid,
        amount=float(expense.amount),
        description=expense.description,
    )
    repo.add(domain_expense)

    return ExpenseRead.from_orm(domain_expense)


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)) -> list[ExpenseRead]:
    repo = SQLAlchemyExpenseRepository(db)
    expenses = repo.list_all()
    return [ExpenseRead.from_orm(e) for e in expenses]


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: UUID, db: Session = Depends(get_db)) -> ExpenseRead:
    # FastAPI handles UUID validation automatically.
    repo = SQLAlchemyExpenseRepository(db)
    exp = repo.get(expense_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseRead.from_orm(exp)
