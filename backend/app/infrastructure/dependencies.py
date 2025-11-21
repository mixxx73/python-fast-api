from typing import Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from ..domain.models import User
from ..domain.services import build_user_service
from .database import get_db
from .repositories import (
    SQLAlchemyExpenseRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)


def get_user_repo(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_group_repo(db: Session = Depends(get_db)) -> SQLAlchemyGroupRepository:
    return SQLAlchemyGroupRepository(db)


def get_expense_repo(db: Session = Depends(get_db)) -> SQLAlchemyExpenseRepository:
    return SQLAlchemyExpenseRepository(db)


def get_user_service(db: Session = Depends(get_db)) -> Callable[[User, UUID], User]:
    user_repo = SQLAlchemyUserRepository(db)
    group_repo = SQLAlchemyGroupRepository(db)
    return build_user_service(user_repo, group_repo, db)
