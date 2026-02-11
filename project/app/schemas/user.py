"""Pydantic schemas with strict validation/sanitization rules."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import sanitize_text


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    bio: str | None = Field(default=None, max_length=500)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if len(cleaned) < 2:
            raise ValueError("full_name must be at least 2 chars after sanitization")
        return cleaned

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return sanitize_text(value)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    bio: str | None = Field(default=None, max_length=500)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = sanitize_text(value)
        if len(cleaned) < 2:
            raise ValueError("full_name must be at least 2 chars after sanitization")
        return cleaned

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return sanitize_text(value)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
