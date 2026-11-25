from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_current_user, get_db, require_admin
from core.security import REFRESH_TOKEN_EXPIRE_DAYS
from models.users_model import User, UserRole
from schemas.users_schemas import (
    TokenResponse,
    UserAdminUpdate,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from services import users_service

router = APIRouter()


def _raise_service_error(exc: users_service.UserServiceError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new customer account."""
    try:
        return await users_service.register_user(db, payload)
    except users_service.UserServiceError as exc:
        _raise_service_error(exc)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user, set HTTP-only refresh cookie, and return tokens."""
    try:
        user, tokens = await users_service.authenticate_user(db, payload)
    except users_service.UserServiceError as exc:
        _raise_service_error(exc)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the currently authenticated user's profile."""
    return current_user


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    """List all users (admin only)."""
    return await users_service.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_single_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Get a single user by ID (owner or admin)."""
    try:
        return await users_service.get_user_for_actor(db, user_id, current_user)
    except users_service.UserServiceError as exc:
        _raise_service_error(exc)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Update a user profile (owner updates basic fields; admin may update role/status)."""
    effective_payload: UserUpdate | UserAdminUpdate = (
        payload
        if current_user.role == UserRole.ADMIN
        else UserUpdate(**payload.model_dump(exclude_unset=True))
    )
    try:
        return await users_service.update_user(db, user_id, effective_payload, current_user)
    except users_service.UserServiceError as exc:
        _raise_service_error(exc)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a user account (owner or admin)."""
    try:
        await users_service.delete_user(db, user_id, current_user)
    except users_service.UserServiceError as exc:
        _raise_service_error(exc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
