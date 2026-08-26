"""
Step 2 & 4 — Authentication Router
Endpoints:
  POST /auth/register  — create a new user account
  POST /auth/login     — authenticate and return JWT token
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── Step 2: Register ────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    - **username**: 3–50 alphanumeric characters
    - **email**: valid email address (must be unique)
    - **password**: minimum 8 characters (stored as bcrypt hash)
    """
    # Check for duplicate email
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Check for duplicate username
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken",
        )

    # Step 3: Hash the password before saving
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ─── Step 4: Login ───────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive an access token",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with username/password and receive a JWT Bearer token.
    Use the returned `access_token` in the `Authorization: Bearer <token>` header.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


# ─── Convenience: current user profile ──────────────────────────────────────
@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current authenticated user",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
