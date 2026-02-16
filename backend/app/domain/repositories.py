"""Abstract repository interfaces defining the persistence contract."""

from abc import ABC, abstractmethod
from typing import Iterable, Optional
from uuid import UUID

from .models import Expense, Group, User


class UserRepository(ABC):
    """Abstract interface for user persistence."""

    @abstractmethod
    async def add(self, user: User) -> User:
        """Persist a new user."""

    @abstractmethod
    async def get(self, user_id: UUID) -> Optional[User]:
        """Return a user by identifier."""


class GroupRepository(ABC):
    """Abstract interface for group persistence."""

    @abstractmethod
    async def add(self, group: Group) -> Group:
        """Persist a new group."""

    @abstractmethod
    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        """Add a member to a group."""

    @abstractmethod
    async def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        """Return groups a user belongs to."""

    # Optional extras
    async def update_name(
        self, _group_id: UUID, _name: str
    ) -> None:  # pragma: no cover - optional in interface
        raise NotImplementedError


class ExpenseRepository(ABC):
    """Abstract interface for expense persistence."""

    @abstractmethod
    async def add(self, expense: Expense) -> Expense:
        """Persist a new expense."""

    @abstractmethod
    async def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
        """Return expenses for a group."""
