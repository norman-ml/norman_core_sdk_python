from norman_objects.services.authenticate.register.register_auth_factor_request import RegisterAuthFactorRequest
from norman_objects.services.authenticate.register.register_email_request import RegisterEmailRequest
from norman_objects.services.authenticate.register.register_password_request import RegisterPasswordRequest
from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import ApiClient


class Register:
    @staticmethod
    async def get_authentication_factors(api_client: ApiClient, token: Sensitive[str], account_id: str):
        response = await api_client.get(f"authenticate/register/get/authentication/factors/{account_id}", token)
        return AccountAuthenticationMethods.model_validate(response)

    @staticmethod
    async def generate_api_key(api_client: ApiClient, token: Sensitive[str], register_key_request: RegisterAuthFactorRequest):
        api_key = await api_client.post("authenticate/generate/key", token, json=register_key_request.model_dump(mode="json"))
        return api_key

    @staticmethod
    async def register_password(api_client: ApiClient, token: Sensitive[str], register_password_request: RegisterPasswordRequest):
        await api_client.post("authenticate/register/password", token, json=register_password_request.model_dump(mode="json"))

    @staticmethod
    async def register_email(api_client: ApiClient, token: Sensitive[str], register_email_request: RegisterEmailRequest):
        await api_client.post("authenticate/register/email", token, json=register_email_request.model_dump(mode="json"))


    @staticmethod
    async def verify_email(api_client: ApiClient, token: Sensitive[str], email: str, code: str):
        await api_client.post(f"authenticate/register/email/verify/{email}/{code}", token)

    @staticmethod
    async def resend_email_otp(api_client: ApiClient, token: Sensitive[str], resend_email_verification_code_request: ResendEmailVerificationCodeRequest):
        await api_client.post("authenticate/register/email/resend/otp", token, json=resend_email_verification_code_request.model_dump(mode="json"))
