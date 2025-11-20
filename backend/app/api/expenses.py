from datetime import datetime, timezone
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


def _as_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, str):
        try:
            v = value.replace("Z", "+00:00")

            return datetime.fromisoformat(v)
        except Exception:
            pass

    return datetime.now(timezone.utc)


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

    member_ids = group.members
    if pid not in member_ids:
        raise HTTPException(
            status_code=400, detail="Payer is not a member of the group"
        )

    repo = SQLAlchemyExpenseRepository(db)
    e = Expense(
        group_id=gid,
        payer_id=pid,
        amount=float(expense.amount),
        description=expense.description,
    )
    repo.add(e)
    return ExpenseRead(
        id=e.id,
        group_id=e.group_id,
        payer_id=e.payer_id,
        amount=e.amount,
        created_at=_as_datetime(e.created_at),
        description=e.description,
    )


@router.get("/", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)) -> list[ExpenseRead]:
    repo = SQLAlchemyExpenseRepository(db)
    return [
        ExpenseRead(
            id=e.id,
            group_id=e.group_id,
            payer_id=e.payer_id,
            amount=e.amount,
            created_at=_as_datetime(e.created_at),
            description=e.description,
        )
        for e in repo.list_all()
    ]


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: str, db: Session = Depends(get_db)) -> ExpenseRead:
    try:
        eid = UUID(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    repo = SQLAlchemyExpenseRepository(db)
    exp = repo.get(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    return ExpenseRead(
        id=exp.id,
        group_id=exp.group_id,
        payer_id=exp.payer_id,
        amount=exp.amount,
        created_at=_as_datetime(exp.created_at),
        description=exp.description,
    )
