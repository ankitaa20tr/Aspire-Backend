from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from app.database.database import get_db
from app.database.models import User
from app.schemas.user import TokenData
from loguru import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Checks if the plain text password matches the hashed password in the DB.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hashes the password using bcrypt.
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verifies if the provided password is correct.
def create_access_token(data: dict) -> str:
    payload = data.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiration_time})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Retrieves the current user from the token.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # If token is invalid, this exception will be raised
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if not email or not user_id:
            logger.warning("Missing 'sub' or 'user_id' in token.")
            raise invalid_credentials_exception

        token_data = TokenData(email=email, user_id=user_id)

    except JWTError as e:
        logger.error(f"JWT decoding failed: {e}")
        raise invalid_credentials_exception

    # Fetch the user from the database using the ID from the token
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        logger.warning(f"User not found: {token_data.email}")
        raise invalid_credentials_exception

    return user

# Checks if the user is active.
def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account is inactive.",
        )
    return current_user

if __name__ == "__main__":
    print("Authetication working")

    # source venvAnkitaTiwari/bin/activate
    # python3 -m app.auth.utils
