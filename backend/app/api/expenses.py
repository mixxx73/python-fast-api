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

    group = group_repo.get(gid)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not user_repo.get(pid):
        raise HTTPException(status_code=404, detail="Payer not found")

    # Validation: Check if the payer is a member of the group.
    member_ids = [m.id for m in group.members]
    if pid not in member_ids:
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

    return ExpenseRead.model_validate(domain_expense)


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)) -> list[ExpenseRead]:
    """List all expenses."""
    repo = SQLAlchemyExpenseRepository(db)
    expenses = repo.list_all()
    return [ExpenseRead.model_validate(e) for e in expenses]


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: UUID, db: Session = Depends(get_db)) -> ExpenseRead:
    """Get a specific expense by its ID."""
    repo = SQLAlchemyExpenseRepository(db)
    exp = repo.get(expense_id)

    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    return ExpenseRead.model_validate(exp)
