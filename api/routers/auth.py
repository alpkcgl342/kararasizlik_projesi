"""`/api/auth/*` — kayıt ol / giriş yap / çıkış yap / mevcut kullanıcı."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_
from sqlmodel import Session, select

from api.auth import (
    ACCESS_TOKEN_COOKIE_NAME,
    create_access_token,
    hash_password,
    verify_password,
)
from api.config import get_settings
from api.database import get_session
from api.deps import get_current_user_optional
from api.models import User
from api.schemas import LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()

COOKIE_MAX_AGE_SECONDS = settings.jwt_expire_minutes * 60


def _set_auth_cookie(response: Response, user_id: int) -> None:
    token = create_access_token(user_id)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, response: Response, session: Session = Depends(get_session)):
    existing = session.exec(
        select(User).where(or_(User.username == body.username, User.email == body.email))
    ).first()
    if existing is not None:
        # Hangi alanın çakıştığını belirtmiyoruz: aksi halde bu endpoint, başka bir
        # kullanıcının e-postasının sistemde kayıtlı olup olmadığını (user enumeration)
        # ifşa eden bir yan kanala dönüşür.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kullanıcı adı veya e-posta zaten kullanımda",
        )

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Kayıt sonrası kullanıcıyı doğrudan giriş yapmış say (ekstra bir login isteği gerekmesin).
    _set_auth_cookie(response, user.id)

    return user


@router.post("/login", response_model=UserRead)
def login(body: LoginRequest, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya parola hatalı",
        )

    _set_auth_cookie(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME, path="/")


@router.get("/me")
def me(user: User | None = Depends(get_current_user_optional)):
    if user is None:
        return {"user": None}
    return {"user": UserRead.model_validate(user)}
