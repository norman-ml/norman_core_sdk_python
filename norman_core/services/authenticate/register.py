from norman_objects.services.authenticate.register.register_auth_factor_request import RegisterAuthFactorRequest
from norman_objects.services.authenticate.register.register_email_request import RegisterEmailRequest
from norman_objects.services.authenticate.register.register_password_request import RegisterPasswordRequest
from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods
from norman_objects.shared.security.sensitive import Sensitive

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Register(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_authentication_factors(self, token: Sensitive[str], account_id: str) -> AccountAuthenticationMethods:
        response = await self._http_client.get(f"authenticate/register/get/authentication/factors/{account_id}", token)
        return AccountAuthenticationMethods.model_validate(response)

    async def generate_api_key(self, token: Sensitive[str], register_key_request: RegisterAuthFactorRequest) -> str:
        json = register_key_request.model_dump(mode="json")
        api_key = await self._http_client.post("authenticate/generate/key", token, json=json)
        return api_key

    async def register_password(self, token: Sensitive[str], register_password_request: RegisterPasswordRequest) -> None:
        json = register_password_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/password", token, json=json)

    async def register_email(self, token: Sensitive[str], register_email_request: RegisterEmailRequest) -> None:
        json = register_email_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/email", token, json=json)

    async def verify_email(self, token: Sensitive[str], email: str, code: str) -> None:
        await self._http_client.post(f"authenticate/register/email/verify/{email}/{code}", token)

    async def resend_email_otp(self, token: Sensitive[str], resend_email_verification_code_request: ResendEmailVerificationCodeRequest) -> None:
        json = resend_email_verification_code_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/email/resend/otp", token, json=json)
