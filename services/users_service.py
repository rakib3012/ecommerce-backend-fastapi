from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_token_pair, hash_password, verify_password
from models.users_model import User, UserRole
from schemas.users_schemas import UserAdminUpdate, UserCreate, UserLogin, UserUpdate


class UserServiceError(Exception):
    """Domain error raised by user service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def register_user(db: AsyncSession, payload: UserCreate) -> User:
    """Register a new customer user with hashed password and uniqueness checks."""
    email = payload.email.strip().lower()
    mobile = payload.mobile.strip()

    existing = await db.execute(
        select(User).where(or_(User.email == email, User.mobile == mobile))
    )
    if existing.scalar_one_or_none() is not None:
        raise UserServiceError(
            status_code=409,
            detail="A user with this email or mobile number already exists.",
        )

    user = User(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=email,
        mobile=mobile,
        password_hash=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as exc:
        await db.rollback()
        raise UserServiceError(
            status_code=409,
            detail="A user with this email or mobile number already exists.",
        ) from exc

    return user


async def authenticate_user(
    db: AsyncSession,
    payload: UserLogin,
) -> tuple[User, dict[str, str]]:
    """Authenticate user credentials and issue access/refresh JWT pair."""
    email = payload.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise UserServiceError(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise UserServiceError(
            status_code=403,
            detail="User account is inactive.",
        )

    tokens = create_token_pair(subject=user.id, role=user.role.value)
    return user, tokens


async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[User]:
    """Return a paginated list of users ordered by ID."""
    result = await db.execute(
        select(User).order_by(User.id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """Fetch a single user by ID or raise 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UserServiceError(status_code=404, detail="User not found.")
    return user


def _ensure_owner_or_admin(target_user_id: int, current_user: User) -> None:
    """Enforce that the caller owns the target user or is an ADMIN."""
    if current_user.id != target_user_id and current_user.role != UserRole.ADMIN:
        raise UserServiceError(
            status_code=403,
            detail="You do not have permission to access this user.",
        )


async def get_user_for_actor(
    db: AsyncSession,
    user_id: int,
    current_user: User,
) -> User:
    """Fetch a user by ID after verifying owner or admin access."""
    _ensure_owner_or_admin(user_id, current_user)
    return await get_user_by_id(db, user_id)


async def update_user(
    db: AsyncSession,
    user_id: int,
    payload: UserUpdate | UserAdminUpdate,
    current_user: User,
) -> User:
    """Update user fields with owner/admin authorization."""
    _ensure_owner_or_admin(user_id, current_user)
    user = await get_user_by_id(db, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    if current_user.role != UserRole.ADMIN:
        for restricted in ("role", "is_active", "is_verified"):
            update_data.pop(restricted, None)

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as exc:
        await db.rollback()
        raise UserServiceError(
            status_code=409,
            detail="Updated mobile number conflicts with an existing user.",
        ) from exc

    return user


async def delete_user(
    db: AsyncSession,
    user_id: int,
    current_user: User,
) -> None:
    """Delete a user account after verifying owner or admin access."""
    _ensure_owner_or_admin(user_id, current_user)
    user = await get_user_by_id(db, user_id)
    await db.delete(user)
    await db.commit()
