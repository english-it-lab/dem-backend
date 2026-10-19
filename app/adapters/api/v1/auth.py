from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.api.dependencies import get_auth_service, get_current_user
from app.schemas import (
    EmailCodeRequest,
    LoginRequest,
    LoginResponse,
)
from app.services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.post("/request-code", status_code=status.HTTP_204_NO_CONTENT)
async def generate_email_code(
    payload: EmailCodeRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    result = await service.send_verification_code(payload)

    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot send verification code")


@router.post("/login")
async def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    result = await service.login(payload)

    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return LoginResponse.model_validate({"access_token": result})


@router.get("/ping")
async def ping(user_id: Annotated[int, Depends(get_current_user)]) -> None:
    pass
