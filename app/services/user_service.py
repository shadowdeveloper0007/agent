"""Business logic for user CRUD operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.helpers import apply_partial_update


class UserService:
    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        existing = db.scalar(select(User).where(User.email == payload.email))
        if existing:
            raise ValueError("Email is already registered")

        user = User(email=payload.email, full_name=payload.full_name, bio=payload.bio)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def list_users(db: Session, *, page: int, page_size: int) -> tuple[list[User], int]:
        total = db.query(User).count()
        offset = (page - 1) * page_size
        users = db.query(User).offset(offset).limit(page_size).all()
        return users, total

    @staticmethod
    def update_user(db: Session, user: User, payload: UserUpdate) -> User:
        updates = payload.model_dump(exclude_unset=True)
        if "email" in updates:
            existing = db.scalar(select(User).where(User.email == updates["email"], User.id != user.id))
            if existing:
                raise ValueError("Email is already registered")

        apply_partial_update(user, updates)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()
