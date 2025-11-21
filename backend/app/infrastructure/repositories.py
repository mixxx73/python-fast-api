from typing import Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..domain.models import Expense, Group, User
from ..domain.repositories import ExpenseRepository, GroupRepository, UserRepository
from .orm import ExpenseORM, GroupORM, UserORM


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: Dict[UUID, User] = {}

    def add(self, user: User) -> None:
        self.users[user.id] = user

    def get(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)


class InMemoryGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self.groups: Dict[UUID, Group] = {}

    def add(self, group: Group) -> None:
        self.groups[group.id] = group

    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        group = self.groups[group_id]
        group.members.append(user_id)

    def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        return [g for g in self.groups.values() if user_id in g.members]

    def update_name(self, group_id: UUID, name: str) -> None:
        if group_id in self.groups:
            g = self.groups[group_id]
            g.name = name


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self) -> None:
        self.expenses: Dict[UUID, Expense] = {}

    def add(self, expense: Expense) -> None:
        self.expenses[expense.id] = expense

    def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
        return [e for e in self.expenses.values() if e.group_id == group_id]


def _to_user_model(row: UserORM) -> User:
    return User(id=row.id, email=row.email, name=row.name, is_admin=row.is_admin)


def _to_group_model(row: GroupORM) -> Group:
    member_ids: List[UUID] = [u.id for u in row.members]
    return Group(id=row.id, name=row.name, members=member_ids)


def _to_expense_model(row: ExpenseORM) -> Expense:
    return Expense(
        id=row.id,
        group_id=row.group_id,
        payer_id=row.payer_id,
        amount=row.amount,
        created_at=row.created_at,
        description=row.description,
    )


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, user: User) -> None:
        row = UserORM(
            id=user.id, email=user.email, name=user.name, is_admin=user.is_admin
        )
        self.db.add(row)
        self.db.commit()

    def get(self, user_id: UUID) -> Optional[User]:
        row = self.db.get(UserORM, user_id)
        if not row:
            return None
        return _to_user_model(row)

    # Extra helper not in interface
    def list_all(self) -> Iterable[User]:
        rows = self.db.query(UserORM).all()
        return [_to_user_model(r) for r in rows]

    def get_by_email(self, email: str) -> Optional[User]:
        row = self.db.query(UserORM).filter(UserORM.email == email).first()
        if not row:
            return None
        return _to_user_model(row)

    def add_with_password(self, user: User, password_hash: str) -> None:
        row = UserORM(
            id=user.id,
            email=user.email,
            name=user.name,
            password_hash=password_hash,
            is_admin=user.is_admin,
        )
        self.db.add(row)
        self.db.commit()


class SQLAlchemyGroupRepository(GroupRepository):
    def         __init__(self, db: Session) -> None:
        self.db = db

    def add(self, group: Group) -> None:
        row = GroupORM(id=group.id, name=group.name)
        self.db.add(row)
        self.db.commit()

    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        group = self.db.get(GroupORM, group_id)
        user = self.db.get(UserORM, user_id)
        if group and user:
            group.members.append(user)
            self.db.commit()

    def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        user = self.db.get(UserORM, user_id)
        if not user:
            return []
        # Access relationship; SQLAlchemy loads members' groups
        groups = user.groups
        return [_to_group_model(g) for g in groups]

    # Extra helpers not in interface
    def get(self, group_id: UUID) -> Optional[Group]:
        row = self.db.get(GroupORM, group_id)
        if not row:
            return None
        return _to_group_model(row)

    def list_all(self) -> Iterable[Group]:
        rows = self.db.query(GroupORM).all()
        return [_to_group_model(r) for r in rows]

    def update_name(self, group_id: UUID, name: str) -> None:
        row = self.db.get(GroupORM, group_id)
        if row:
            row.name = name
            self.db.commit()


class SQLAlchemyExpenseRepository(ExpenseRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, expense: Expense) -> ExpenseORM:
        row = ExpenseORM(
            id=expense.id,
            group_id=expense.group_id,
            payer_id=expense.payer_id,
            amount=expense.amount,
            created_at=expense.created_at,
            description=expense.description,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
        rows = self.db.query(ExpenseORM).filter(ExpenseORM.group_id == group_id).all()
        return [_to_expense_model(r) for r in rows]

    # Extra helpers not in interface
    def get(self, expense_id: UUID) -> Optional[Expense]:
        row = self.db.get(ExpenseORM, expense_id)
        if not row:
            return None
        return _to_expense_model(row)

    def list_all(self) -> Iterable[Expense]:
        rows = self.db.query(ExpenseORM).all()
        return [_to_expense_model(r) for r in rows]
