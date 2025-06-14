from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.models import User, PasswordResetToken
from app.auth.schemas import UserSignup, UserSignin, ForgotPassword, ResetPassword, UserResponse, TokenResponse
from app.auth.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, generate_reset_token
from app.utils.email import send_reset_email
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """User signup endpoint"""
    logger.info(f"Signup attempt for email: {user_data.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Signup failed - email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Email already registered.", "code": 400}
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User created successfully.")
    return new_user

@router.post("/signin", response_model=TokenResponse)
async def signin(user_data: UserSignin, db: Session = Depends(get_db)):
    """User signin endpoint"""
    logger.info(f"Signin attempt for email: {user_data.email}")
    
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        logger.warning(f"Signin failed - invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": True, "message": "Invalid email or password", "code": 401}
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info(f"User signed in successfully.")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPassword, db: Session = Depends(get_db)):
    """Forgot password endpoint"""
    logger.info(f"Forgot password request for email: {request.email}")
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Email not found", "code": 404}
        )
    
    # Generate reset token
    reset_token = generate_reset_token()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    
    # Save reset token
    reset_token_obj = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expiration_time=expiration_time
    )
    db.add(reset_token_obj)
    db.commit()
    
    # Send email
    await send_reset_email(user.email, reset_token)
    
    logger.info(f"Password reset token generated for user: {request.email}")
    return {"message": "Password reset link has been sent. Please check your email."}

@router.post("/reset-password")
async def reset_password(request: ResetPassword, db: Session = Depends(get_db)):
    """Reset password endpoint"""
    logger.info(f"Password reset attempt with token")
    
    # Find and validate token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expiration_time > datetime.now(timezone.utc)
    ).first()
    
    if not reset_token:
        logger.warning(f"Invalid or expired reset token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Invalid or expired reset token", "code": 400}
        )
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    reset_token.used = True
    
    db.commit()
    
    logger.info(f"Password reset successfully for user: {user.email}")
    return {"message": "Password reset successfully"}