from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import User, APIKey
import secrets


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        """Create new user"""
        hashed_password = AuthService.get_password_hash(password)

        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def create_api_key(db: Session, user_id: int, name: str = None, rate_limit: int = 100) -> APIKey:
        """Create new API key"""
        key = f"sk_{secrets.token_urlsafe(32)}"

        api_key = APIKey(
            user_id=user_id,
            key=key,
            name=name,
            rate_limit=rate_limit
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        return api_key

    @staticmethod
    def verify_api_key(db: Session, api_key: str) -> Optional[APIKey]:
        """Verify API key"""
        key = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == 1
        ).first()

        if key:
            # Update last used
            key.last_used_at = datetime.utcnow()
            db.commit()

        return key


# Global instance
auth_service = AuthService()
