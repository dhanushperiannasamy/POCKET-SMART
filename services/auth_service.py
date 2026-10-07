"""
Authentication and Session Security Service for PocketSmart AI.
Matches PDF pages 10, 11, 18-20, 24.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
import hashlib
import hmac

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models.user import UserInDB, Token, TokenData
from models.session import UserSession

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_pocketsmart_ai_2025")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    pwd_context = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "users_db.json")
users_db: Dict[str, UserInDB] = {}
active_sessions: Dict[str, UserSession] = {}
blacklisted_tokens: Set[str] = set()


def _fallback_hash(password: str) -> str:
    salt = "pocketsmart_salt_val"
    return "pbkdf2$" + hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _fallback_verify(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(_fallback_hash(plain), hashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    if hashed_password.startswith("pbkdf2$"):
        return _fallback_verify(plain_password, hashed_password)
    return False


def get_password_hash(password: str) -> str:
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    return _fallback_hash(password)


def load_users():
    """Loads users from local json file if exists, else seeds default demo user."""
    global users_db
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for uname, udata in data.items():
                    users_db[uname] = UserInDB(**udata)
        except Exception:
            pass

    if "demouser" not in users_db:
        demo_user = UserInDB(
            username="demouser",
            email="demo@pocketsmart.ai",
            full_name="Demo User",
            hashed_password=get_password_hash("password123"),
            disabled=False
        )
        users_db["demouser"] = demo_user
        save_users()


def save_users():
    """Saves users to local json file."""
    try:
        data = {uname: u.dict() for uname, u in users_db.items()}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


load_users()


def authenticate_user(db: Dict[str, UserInDB], username: str, password: str) -> Optional[UserInDB]:
    user = db.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_token(request: Request) -> Optional[str]:
    """Extracts JWT token from Authorization header or 'access_token' cookie."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token.split(" ")[1]
        return cookie_token
    return None


async def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UserInDB]:
    if not token:
        token = await get_token(request)
    if not token:
        return None
    if token in blacklisted_tokens:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
        
    user = users_db.get(token_data.username)
    if user is None:
        return None
    
    if username in active_sessions:
        active_sessions[username].last_activity = datetime.utcnow()
        
    return user


async def get_current_active_user(current_user: Optional[UserInDB] = Depends(get_current_user)) -> UserInDB:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_optional_current_user(request: Request) -> Optional[UserInDB]:
    """Returns current authenticated user if token present, or None if guest."""
    try:
        token = await get_token(request)
        if token:
            return await get_current_user(request, token)
    except Exception:
        pass
    return None

