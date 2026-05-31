from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    display_name: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
) -> CurrentUser:
    if credentials is not None:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

        user_id = payload.get("sub")
        if user_id is None or not str(user_id).strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user id",
            )

        display_name = str(
            x_user_name
            or payload.get("username")
            or payload.get("preferred_username")
            or user_id
        ).strip()
        return CurrentUser(user_id=str(user_id), display_name=display_name)

    # Temporary compatibility for manual testing until frontend switches to JWT.
    if x_user_id is None or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization bearer token is required",
        )

    user_id = x_user_id.strip()
    return CurrentUser(user_id=user_id, display_name=(x_user_name or user_id).strip())


def get_current_user_id(current_user: CurrentUser = Depends(get_current_user)) -> str:
    return current_user.user_id


def verify_internal_service_token(
    x_internal_service_token: str | None = Header(default=None),
) -> None:
    if not settings.internal_service_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal service token is not configured",
        )

    if x_internal_service_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal service token is required",
        )

    if x_internal_service_token != settings.internal_service_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token",
        )
