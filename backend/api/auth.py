import secrets
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from auth.security import create_access_token, hash_password, verify_password
from database.config import settings
from database.session import get_db
from models.entities import MLToken, User
from models.schemas import LoginRequest, MLTokenResponse, RegisterRequest, TokenResponse, UserResponse
from services.email_service import send_welcome_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    user = User(email=payload.email, phone=payload.phone, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    if not settings.academic_mode:
        send_welcome_email(user.email)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user


_oauth_states: dict[str, int] = {}


@router.get("/ml/login")
def ml_login(user: User = Depends(get_current_user)):
    if not settings.ml_client_id or not settings.ml_client_secret:
        raise HTTPException(status_code=400, detail="ML_CLIENT_ID y ML_CLIENT_SECRET no configurados en .env")

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = user.id

    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={settings.ml_client_id}"
        f"&redirect_uri={settings.backend_public_url}/api/auth/ml/callback"
        f"&state={state}"
    )
    return {"url": auth_url}


@router.get("/ml/callback")
async def ml_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    user_id = _oauth_states.pop(state, None)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    token_url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.ml_client_id,
        "client_secret": settings.ml_client_secret,
        "code": code,
        "redirect_uri": f"{settings.backend_public_url}/api/auth/ml/callback",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)

    if resp.status_code != 200:
        return RedirectResponse(
            url=f"{settings.frontend_url}/ml/callback?error=oauth_error&detail={resp.text[:200]}",
        )

    token_data = resp.json()
    expires_in = token_data.get("expires_in", 21600)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    existing = db.query(MLToken).filter(MLToken.user_id == user_id).first()
    if existing:
        existing.access_token = token_data["access_token"]
        existing.refresh_token = token_data.get("refresh_token", existing.refresh_token)
        existing.expires_at = expires_at
    else:
        ml_token = MLToken(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            expires_at=expires_at,
        )
        db.add(ml_token)

    db.commit()

    return RedirectResponse(url=f"{settings.frontend_url}/ml/callback?success=1")


@router.get("/ml/token-info", response_model=MLTokenResponse)
def ml_token_info(user: User = Depends(get_current_user)):
    token = user.ml_tokens[0] if user.ml_tokens else None
    if not token:
        raise HTTPException(status_code=404, detail="No hay token de ML. Conectá tu cuenta de MercadoLibre.")
    return MLTokenResponse(
        is_connected=True,
        has_refresh_token=bool(token.refresh_token),
        expires_at=token.expires_at,
        user_id=user.id,
    )


@router.post("/ml/disconnect")
def ml_disconnect(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(MLToken).filter(MLToken.user_id == user.id).delete()
    db.commit()
    return {"status": "disconnected"}
