"""Router'lar arasında paylaşılan FastAPI dependency'leri."""
from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session

from api.auth import ACCESS_TOKEN_COOKIE_NAME, decode_access_token
from api.database import get_session
from api.models import User


def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_TOKEN_COOKIE_NAME),
    session: Session = Depends(get_session),
) -> User:
    """Giriş zorunlu endpoint'ler için: cookie yoksa/geçersizse 401 döner."""
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Giriş yapmanız gerekiyor")

    user_id = decode_access_token(access_token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum geçersiz veya süresi dolmuş")

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    return user


def get_current_user_optional(
    access_token: str | None = Cookie(default=None, alias=ACCESS_TOKEN_COOKIE_NAME),
    session: Session = Depends(get_session),
) -> User | None:
    """Oylama gibi hem üye hem misafirin erişebildiği endpoint'ler için."""
    if access_token is None:
        return None
    user_id = decode_access_token(access_token)
    if user_id is None:
        return None
    return session.get(User, user_id)
