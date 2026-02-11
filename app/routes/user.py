"""User API routes."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: Request, payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    del request  # request kept for rate-limiter dependency compatibility
    try:
        return UserService.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserResponse)
def get_user(request: Request, user_id: int = Path(..., ge=1), db: Session = Depends(get_db)) -> UserResponse:
    del request
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=dict)
def list_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    del request
    users, total = UserService.list_users(db, page=page, page_size=page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [UserResponse.model_validate(user).model_dump() for user in users],
    }


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    request: Request,
    payload: UserUpdate,
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> UserResponse:
    del request
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        return UserService.update_user(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(request: Request, user_id: int = Path(..., ge=1), db: Session = Depends(get_db)) -> None:
    del request
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    UserService.delete_user(db, user)
