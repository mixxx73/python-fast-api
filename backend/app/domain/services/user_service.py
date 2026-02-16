from typing import Callable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..exceptions import UserExistsError
from ..models import User
from ..repositories import GroupRepository, UserRepository


def create_user_and_add_to_group(
    user: User,
    *,
    group_id: UUID,
    user_repo: UserRepository,
    group_repo: GroupRepository,
    db: Session,
) -> User:
    """Create a user and add them to a group in a single unit of work."""
    try:
        created_user = user_repo.add(user)
    except UserExistsError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise UserExistsError(f"Failed to create user {user.email}") from exc

    try:
        group_repo.add_member(group_id, created_user.id)
    except Exception:
        db.rollback()
        raise

    return created_user


def build_user_service(
    user_repo: UserRepository, group_repo: GroupRepository, db: Session
) -> Callable[[User, UUID], User]:
    """Provide a callable suitable for dependency injection."""

    def service(user: User, group_id: UUID) -> User:
        return create_user_and_add_to_group(
            user, group_id=group_id, user_repo=user_repo, group_repo=group_repo, db=db
        )

    return service
