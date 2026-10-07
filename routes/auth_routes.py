"""
Authentication Routes for PocketSmart AI.
Implements /register, /login, /logout, /token as per PDF pages 18-19.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from models.user import RegisterUser, UserInDB, Token
from models.session import UserSession
from services.auth_service import (
    users_db,
    active_sessions,
    blacklisted_tokens,
    authenticate_user,
    create_access_token,
    get_password_hash,
    save_users,
    get_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page as per PDF page 18."""
    try:
        token = await get_token(request)
        if token:
            user = await get_current_user(request, token)
            if user:
                return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception:
        pass
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"title": "Sign In - PocketSmart AI"}
    )


@router.post("/login")
async def login_submit(request: Request):
    """Processes login form or JSON submission."""
    content_type = request.headers.get("content-type", "")
    is_json = "application/json" in content_type

    if is_json:
        try:
            data = await request.json()
            username = data.get("username", "").strip()
            password = data.get("password", "")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    else:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))

    user = authenticate_user(users_db, username, password)
    if not user:
        if is_json:
            raise HTTPException(status_code=400, detail="Invalid username or password.")
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password. Please try again.",
                "title": "Sign In - PocketSmart AI",
            },
            status_code=400,
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    existing_user_data = {}
    if user.username in active_sessions:
        existing_user_data = active_sessions[user.username].user_data
        old_token = active_sessions[user.username].token
        if old_token:
            blacklisted_tokens.add(old_token)

    active_sessions[user.username] = UserSession(
        username=user.username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=access_token,
        user_data=existing_user_data,
    )

    if is_json:
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer", "username": user.username}
        )
    else:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page as per PDF page 18."""
    try:
        token = await get_token(request)
        if token:
            user = await get_current_user(request, token)
            if user:
                return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception:
        pass
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"title": "Create Account - PocketSmart AI"}
    )


@router.post("/register")
async def register_submit(request: Request):
    """Processes user registration form or JSON."""
    content_type = request.headers.get("content-type", "")
    is_json = "application/json" in content_type

    if is_json:
        try:
            data = await request.json()
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()
            full_name = data.get("full_name", "")
            password = data.get("password", "")
            confirm_password = data.get("confirm_password")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    else:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        email = str(form.get("email", "")).strip()
        full_name = str(form.get("full_name", ""))
        password = str(form.get("password", ""))
        confirm_password = form.get("confirm_password")

    if confirm_password and password != confirm_password:
        if is_json:
            raise HTTPException(status_code=400, detail="Passwords do not match.")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Passwords do not match.",
                "title": "Create Account - PocketSmart AI",
            },
            status_code=400,
        )

    if username in users_db:
        if is_json:
            raise HTTPException(status_code=400, detail=f"Username '{username}' is already registered.")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": f"Username '{username}' is already registered.",
                "title": "Create Account - PocketSmart AI",
            },
            status_code=400,
        )

    hashed_pw = get_password_hash(password)
    new_user = UserInDB(
        username=username,
        email=email,
        full_name=full_name or username,
        hashed_password=hashed_pw,
        disabled=False,
    )
    users_db[username] = new_user
    save_users()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    active_sessions[username] = UserSession(
        username=username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=access_token,
        user_data={},
    )

    if is_json:
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer", "username": username}
        )
    else:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout(request: Request):
    """Terminates session and clears cookie as per PDF page 19."""
    token = await get_token(request)
    if token:
        blacklisted_tokens.add(token)
        try:
            from jose import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username and username in active_sessions:
                del active_sessions[username]
        except Exception:
            pass

    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


@router.get("/logout")
async def logout_get(request: Request):
    return await logout(request)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 token endpoint as per PDF page 19."""
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    existing_user_data = {}
    if user.username in active_sessions:
        existing_user_data = active_sessions[user.username].user_data
        old_token = active_sessions[user.username].token
        if old_token:
            blacklisted_tokens.add(old_token)

    active_sessions[user.username] = UserSession(
        username=user.username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=access_token,
        user_data=existing_user_data,
    )

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
    )
    return response
