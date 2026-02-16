"""Domain-specific exceptions."""


class UserExistsError(Exception):
    """Raised when attempting to create a user with a duplicate email."""


class ExpenseCreateError(Exception):
    """Raised when an expense cannot be persisted."""


class GroupNotFoundError(Exception):
    """Raised when a group cannot be found."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""
