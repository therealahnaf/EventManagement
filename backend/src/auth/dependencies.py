from typing import Any, List

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from src.db.main import get_db
from ..db.models import User

from .service import UserService
from .utils import decode_token
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
)


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        print(f"Token: {token}")

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")
        
class AccessTokenFromCookie:
    def __init__(self):
        pass

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise InvalidToken("Access token not found in cookies")

        token_data = decode_token(token)

        if token_data.get("refresh"):  # if it's a refresh token used where access is needed
            raise AccessTokenRequired()

        return token_data

class RefreshTokenFromCookie:
    def __init__(self):
        pass

    async def __call__(self, request: Request):
        token = request.cookies.get("refresh_token")
        if not token:
            raise InvalidToken("Refresh token not found in cookies")

        token_data = decode_token(token)

        if token_data.get("access"):  # if it's a refresh token used where access is needed
            raise RefreshTokenRequired()

        return token_data

async def get_current_user_with_cookie(
    token_details: dict = Depends(AccessTokenFromCookie()),
    db = Depends(get_db),
):
    print(f"Token details from cookie: {token_details}")
    user_email = token_details["user"]["email"]
    user_service = UserService(db)
    user = await user_service.get_user_by_email(user_email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user_with_cookie)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()