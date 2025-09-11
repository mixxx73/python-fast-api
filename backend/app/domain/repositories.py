from abc import ABC, abstractmethod
from typing import Iterable, Optional
from uuid import UUID

from .models import Expense, Group, User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> None:
        """Persist a new user."""

    @abstractmethod
    def get(self, user_id: UUID) -> Optional[User]:
        """Return a user by identifier."""


class GroupRepository(ABC):
    @abstractmethod
    def add(self, group: Group) -> None:
        """Persist a new group."""

    @abstractmethod
    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        """Add a member to a group."""

    @abstractmethod
    def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        """Return groups a user belongs to."""

    # Optional extras
    def update_name(
        self, group_id: UUID, name: str
    ) -> None:  # pragma: no cover - optional in interface
        raise NotImplementedError


class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> None:
        """Persist a new expense."""

    @abstractmethod
    def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
        """Return expenses for a group."""
