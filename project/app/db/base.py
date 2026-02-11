"""SQLAlchemy base and model imports for metadata creation."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for metadata registration
from app.models.user import User  # noqa: E402,F401
