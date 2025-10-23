from typing import Iterable, Optional
from uuid import UUID, uuid4

import pytest

from app.domain.models import Expense, Group, User
from app.domain.repositories import ExpenseRepository, GroupRepository, UserRepository


# Concrete implementations for testing
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = {}

    def add(self, user: User) -> None:
        self.users[user.id] = user

    def get(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)


class InMemoryGroupRepository(GroupRepository):
    def __init__(self):
        self.groups = {}
        self.memberships = {}  # group_id -> set of user_ids

    def add(self, group: Group) -> None:
        self.groups[group.id] = group
        self.memberships[group.id] = set()

    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        if group_id not in self.memberships:
            self.memberships[group_id] = set()
        self.memberships[group_id].add(user_id)

    def list_for_user(self, user_id: UUID) -> Iterable[Group]:
        return [
            self.groups[group_id]
            for group_id, members in self.memberships.items()
            if user_id in members
        ]

    def update_name(self, group_id: UUID, name: str) -> None:
        if group_id in self.groups:
            self.groups[group_id].name = name


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self):
        self.expenses = []

    def add(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def list_for_group(self, group_id: UUID) -> Iterable[Expense]:
        return [e for e in self.expenses if e.group_id == group_id]


# Fixtures
@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def group_repo():
    return InMemoryGroupRepository()


@pytest.fixture
def expense_repo():
    return InMemoryExpenseRepository()


@pytest.fixture
def sample_user():
    return User(id=uuid4(), name="John Doe", email="john@example.com")


@pytest.fixture
def sample_group():
    return Group(id=uuid4(), name="Trip to Paris")


@pytest.fixture
def sample_expense(sample_group):
    return Expense(
        id=uuid4(),
        group_id=sample_group.id,
        description="Hotel",
        amount=100.0,
        payer_id=uuid4(),
    )


# UserRepository Tests
class TestUserRepository:
    def test_add_user(self, user_repo, sample_user):
        """Test adding a user to the repository."""
        user_repo.add(sample_user)
        retrieved = user_repo.get(sample_user.id)
        assert retrieved is not None
        assert retrieved.id == sample_user.id
        assert retrieved.name == sample_user.name

    def test_get_existing_user(self, user_repo, sample_user):
        """Test retrieving an existing user."""
        user_repo.add(sample_user)
        result = user_repo.get(sample_user.id)
        assert result == sample_user

    def test_get_nonexistent_user(self, user_repo):
        """Test retrieving a user that doesn't exist returns None."""
        nonexistent_id = uuid4()
        result = user_repo.get(nonexistent_id)
        assert result is None

    def test_add_multiple_users(self, user_repo):
        """Test adding multiple users."""
        user1 = User(id=uuid4(), name="Alice", email="alice@example.com")
        user2 = User(id=uuid4(), name="Bob", email="bob@example.com")

        user_repo.add(user1)
        user_repo.add(user2)

        assert user_repo.get(user1.id) == user1
        assert user_repo.get(user2.id) == user2


# GroupRepository Tests
class TestGroupRepository:
    def test_add_group(self, group_repo, sample_group):
        """Test adding a group to the repository."""
        group_repo.add(sample_group)
        assert sample_group.id in group_repo.groups

    def test_add_member_to_group(self, group_repo, sample_group, sample_user):
        """Test adding a member to a group."""
        group_repo.add(sample_group)
        group_repo.add_member(sample_group.id, sample_user.id)

        assert sample_user.id in group_repo.memberships[sample_group.id]

    def test_list_groups_for_user(self, group_repo, sample_user):
        """Test listing groups a user belongs to."""
        group1 = Group(id=uuid4(), name="Group 1")
        group2 = Group(id=uuid4(), name="Group 2")
        group3 = Group(id=uuid4(), name="Group 3")

        group_repo.add(group1)
        group_repo.add(group2)
        group_repo.add(group3)

        group_repo.add_member(group1.id, sample_user.id)
        group_repo.add_member(group3.id, sample_user.id)

        user_groups = list(group_repo.list_for_user(sample_user.id))

        assert len(user_groups) == 2
        assert group1 in user_groups
        assert group3 in user_groups
        assert group2 not in user_groups

    def test_list_groups_for_user_with_no_groups(self, group_repo):
        """Test listing groups for a user not in any groups."""
        user_id = uuid4()
        user_groups = list(group_repo.list_for_user(user_id))
        assert len(user_groups) == 0

    def test_add_multiple_members_to_group(self, group_repo, sample_group):
        """Test adding multiple members to a group."""
        user1_id = uuid4()
        user2_id = uuid4()
        user3_id = uuid4()

        group_repo.add(sample_group)
        group_repo.add_member(sample_group.id, user1_id)
        group_repo.add_member(sample_group.id, user2_id)
        group_repo.add_member(sample_group.id, user3_id)

        assert len(group_repo.memberships[sample_group.id]) == 3

    def test_update_group_name(self, group_repo, sample_group):
        """Test updating a group's name."""
        group_repo.add(sample_group)
        new_name = "Updated Group Name"

        group_repo.update_name(sample_group.id, new_name)

        assert group_repo.groups[sample_group.id].name == new_name

    def test_update_name_raises_not_implemented_by_default(self):
        """Test that update_name raises NotImplementedError in base class."""

        class MinimalGroupRepository(GroupRepository):
            def add(self, group: Group) -> None:
                pass

            def add_member(self, group_id: UUID, user_id: UUID) -> None:
                pass

            def list_for_user(self, user_id: UUID) -> Iterable[Group]:
                return []

        repo = MinimalGroupRepository()
        with pytest.raises(NotImplementedError):
            repo.update_name(uuid4(), "New Name")


# ExpenseRepository Tests
class TestExpenseRepository:
    def test_add_expense(self, expense_repo, sample_expense):
        """Test adding an expense to the repository."""
        expense_repo.add(sample_expense)
        assert sample_expense in expense_repo.expenses

    def test_list_expenses_for_group(self, expense_repo, sample_group):
        """Test listing expenses for a specific group."""
        expense1 = Expense(
            id=uuid4(),
            group_id=sample_group.id,
            description="Lunch",
            amount=50.0,
            payer_id=uuid4(),
        )
        expense2 = Expense(
            id=uuid4(),
            group_id=sample_group.id,
            description="Dinner",
            amount=75.0,
            payer_id=uuid4(),
        )
        other_group_expense = Expense(
            id=uuid4(),
            group_id=uuid4(),
            description="Other",
            amount=100.0,
            payer_id=uuid4(),
        )

        expense_repo.add(expense1)
        expense_repo.add(expense2)
        expense_repo.add(other_group_expense)

        group_expenses = list(expense_repo.list_for_group(sample_group.id))

        assert len(group_expenses) == 2
        assert expense1 in group_expenses
        assert expense2 in group_expenses
        assert other_group_expense not in group_expenses

    def test_list_expenses_for_group_with_no_expenses(self, expense_repo):
        """Test listing expenses for a group with no expenses."""
        group_id = uuid4()
        expenses = list(expense_repo.list_for_group(group_id))
        assert len(expenses) == 0

    def test_add_multiple_expenses(self, expense_repo, sample_group):
        """Test adding multiple expenses."""
        expenses = [
            Expense(
                id=uuid4(),
                group_id=sample_group.id,
                description=f"Expense {i}",
                amount=float(i * 10),
                payer_id=uuid4(),
            )
            for i in range(5)
        ]

        for expense in expenses:
            expense_repo.add(expense)

        assert len(expense_repo.expenses) == 5


# Integration Tests
class TestRepositoryIntegration:
    def test_user_group_expense_workflow(self, user_repo, group_repo, expense_repo):
        """Test a complete workflow with users, groups, and expenses."""
        # Create users
        user1 = User(id=uuid4(), name="Alice", email="alice@example.com")
        user2 = User(id=uuid4(), name="Bob", email="bob@example.com")

        user_repo.add(user1)
        user_repo.add(user2)

        # Create group
        group = Group(id=uuid4(), name="Vacation")
        group_repo.add(group)

        # Add members to group
        group_repo.add_member(group.id, user1.id)
        group_repo.add_member(group.id, user2.id)

        # Create expenses
        expense1 = Expense(
            id=uuid4(),
            group_id=group.id,
            description="Hotel",
            amount=200.0,
            payer_id=user1.id,
        )
        expense2 = Expense(
            id=uuid4(),
            group_id=group.id,
            description="Food",
            amount=150.0,
            payer_id=user2.id,
        )

        expense_repo.add(expense1)
        expense_repo.add(expense2)

        # Verify workflow
        user1_groups = list(group_repo.list_for_user(user1.id))
        assert len(user1_groups) == 1
        assert user1_groups[0].id == group.id

        group_expenses = list(expense_repo.list_for_group(group.id))
        assert len(group_expenses) == 2

        total_expenses = sum(e.amount for e in group_expenses)
        assert total_expenses == 350.0
