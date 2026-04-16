from typing import Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.exceptions import UserExistsError
from ..domain.models import Expense, Group, User
from ..domain.repositories import ExpenseRepository, GroupRepository, UserRepository
from .orm import ExpenseORM, GroupORM, UserORM


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: Dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        self.users[user.id] = user

    async def get(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)


class InMemoryGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self.groups: Dict[UUID, Group] = {}

    async def add(self, group: Group) -> None:
        self.groups[group.id] = group

    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        group = self.groups[group_id]
        group.members.append(user_id)

    async def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        return [g for g in self.groups.values() if user_id in g.members]

    async def update_name(self, _group_id: UUID, _name: str) -> None:
        if _group_id in self.groups:
            g = self.groups[_group_id]
            g.name = _name


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self) -> None:
        self.expenses: Dict[UUID, Expense] = {}

    async def add(self, expense: Expense) -> None:
        self.expenses[expense.id] = expense

    async def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
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
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, user: User) -> UserORM:
        try:
            row = UserORM(
                id=user.id,
                email=user.email,
                name=user.name,
                is_admin=user.is_admin,
                password_hash=user.password_hash,
            )
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
            return row
        except IntegrityError as exc:
            await self.db.rollback()
            raise UserExistsError(f"Failed to create user {user.email}") from exc

    async def get(self, user_id: UUID) -> Optional[UserORM]:
        return await self.db.get(UserORM, user_id)

    # Extra helpers not in interface
    async def list_all(self) -> List[User]:
        result = await self.db.execute(select(UserORM))
        return [_to_user_model(r) for r in result.scalars().all()]

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(UserORM).where(UserORM.email == email))
        row = result.scalar_one_or_none()
        if not row:
            return None
        return _to_user_model(row)


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, group: Group) -> None:
        row = GroupORM(id=group.id, name=group.name)
        self.db.add(row)
        await self.db.commit()

    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        group = await self.db.get(GroupORM, group_id)
        user = await self.db.get(UserORM, user_id)
        if group and user:
            group.members.append(user)
            await self.db.commit()

    async def list_for_user(self, user_id: UUID) -> List[Group]:
        # Load groups and their members in a single async query to avoid
        # triggering lazy loads (which cause MissingGreenlet in async engines).
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await self.db.execute(
            select(GroupORM).join(GroupORM.members).where(UserORM.id == user_id).options(selectinload(GroupORM.members))
        )
        groups = result.scalars().all()
        return [_to_group_model(g) for g in groups]

    # Extra helpers not in interface
    async def get(self, group_id: UUID) -> Optional[Group]:
        row = await self.db.get(GroupORM, group_id)
        if not row:
            return None
        return _to_group_model(row)

    async def list_all(self) -> List[Group]:
        result = await self.db.execute(select(GroupORM))
        return [_to_group_model(r) for r in result.scalars().all()]

    async def update_name(self, _group_id: UUID, _name: str) -> None:
        row = await self.db.get(GroupORM, _group_id)
        if row:
            row.name = _name
            await self.db.commit()


class SQLAlchemyExpenseRepository(ExpenseRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, expense: Expense) -> ExpenseORM:
        row = ExpenseORM(
            id=expense.id,
            group_id=expense.group_id,
            payer_id=expense.payer_id,
            amount=expense.amount,
            created_at=expense.created_at,
            description=expense.description,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_for_group(self, group_id: UUID) -> List[Expense]:
        result = await self.db.execute(select(ExpenseORM).where(ExpenseORM.group_id == group_id))
        return [_to_expense_model(r) for r in result.scalars().all()]

    # Extra helpers not in interface
    async def get(self, expense_id: UUID) -> Optional[Expense]:
        row = await self.db.get(ExpenseORM, expense_id)
        if not row:
            return None
        return _to_expense_model(row)

    async def list_all(self) -> List[Expense]:
        result = await self.db.execute(select(ExpenseORM))
        return [_to_expense_model(r) for r in result.scalars().all()]
