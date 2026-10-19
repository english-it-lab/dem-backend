import time
from datetime import UTC, datetime, timedelta
from http.client import HTTPException

from jose import jwt

from app.core.config import settings
from app.models import Person
from app.schemas import AuthPayload


class JwtService:
    ALGORITHM = "HS256"

    def create_jwt(self, data: dict, ttl_minutes: int) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(UTC) + timedelta(minutes=ttl_minutes)
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=self.ALGORITHM)

    def decode_jwt(self, token: str) -> dict:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[self.ALGORITHM])

    async def create_jwt_from_payload(self, auth_payload: AuthPayload) -> str:
        return jwt.encode(auth_payload.model_dump(), settings.jwt_secret_key, algorithm=self.ALGORITHM)

    async def create_auth_jwt(self, person: Person) -> str:
        expiration_date = int(time.time() + settings.jwt_ttl_minutes * 60)
        return jwt.encode(
            AuthPayload(PERSON_ID=person.id, EXPIRATION_DATE=expiration_date).model_dump(),
            settings.jwt_secret_key,
            algorithm=self.ALGORITHM,
        )

    async def validate_jwt_payload(self, payload: AuthPayload):
        if time.time() > payload.EXPIRATION_DATE:
            raise HTTPException(401, "Expired token")

    async def decode_auth_jwt(self, token: str) -> AuthPayload:
        payload = AuthPayload(**jwt.decode(token, settings.jwt_secret_key, algorithms=[self.ALGORITHM]))
        await self.validate_jwt_payload(payload)
        return payload
