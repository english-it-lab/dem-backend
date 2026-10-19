from app.repositories.person import PersonRepository
from app.schemas import EmailCodeRequest, LoginRequest
from app.services.email_confirmation import EmailConfirmationService
from app.services.jwt import JwtService


class AuthService:
    def __init__(
        self,
        email_service: EmailConfirmationService,
        jwt_service: JwtService,
        person_repository: PersonRepository,
    ) -> None:
        self._email_service = email_service
        self._jwt_service = jwt_service
        self._person_repository = person_repository

    async def send_verification_code(self, payload: EmailCodeRequest) -> bool:
        return await self._email_service.send_code(payload.email)

    async def login(self, payload: LoginRequest) -> str | None:
        email, code = payload.email, payload.code

        correct = self._email_service.verify_code(email, code)
        if not correct:
            return None

        person = await self._person_repository.get_person_by_email(email)
        if person is None:
            person = await self._person_repository.create_person(email)

        return await self._jwt_service.create_auth_jwt(person=person)
