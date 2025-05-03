from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status, BackgroundTasks, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.db.main import get_db

from .dependencies import (
    RefreshTokenFromCookie,
    RoleChecker,
    get_current_user_with_cookie,
)
from .schemas import (
    UserCreateModel,
    UserLoginModel,
    UserResponseModel,
)
from .service import UserService
from .utils import (
    create_access_token,
    verify_password,
)
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken

auth_router = APIRouter()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponseModel)
async def create_user_account(
    user_data: UserCreateModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Create user account using email, password, first_name, last_name
    params:
        user_data: UserCreateModel
    """
    print(f"Creating user account for {user_data.email}")
    user_service = UserService(db)
    print(f"User service created")
    email = user_data.email

    user_exists = await user_service.user_exists(email)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data)
    print(new_user)

    return UserResponseModel(
        id=str(new_user.id),
        email=new_user.email,
        role=new_user.role,
        first_name=new_user.first_name,
        last_name=new_user.last_name
    )

@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    email = login_data.email
    password = login_data.password

    print(f"Logging in user with email: {email}")

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is not None:
        print(f"User found: {user.email}")
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.id),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.id)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Strict",  # or "Lax", depending on your app
            max_age=60 * 15,  # 15 minutes, for example
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=60 * 60 * 24 * 2,  # 2 days
            )

            return {
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.id)},
                }

    raise InvalidCredentials()

@auth_router.get("/me")
async def get_current_user_details(
    user=Depends(get_current_user_with_cookie),
):
    return user

@auth_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenFromCookie())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken