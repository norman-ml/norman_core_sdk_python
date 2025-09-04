from norman_objects.services.authenticate.login.account_id_password_login_request import AccountIDPasswordLoginRequest
from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest
from norman_objects.services.authenticate.login.email_password_login_request import EmailPasswordLoginRequest
from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest

from norman_core.utils.api_client import ApiClient


class Login:
    @staticmethod
    async def login_default(api_client: ApiClient, account_id: str):
        response = await api_client.post(f"authenticate/login/default/{account_id}")
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_with_key(api_client: ApiClient, api_key_login_request: ApiKeyLoginRequest):
        response = await api_client.post("authenticate/login/key", json=api_key_login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_account_id(api_client: ApiClient, login_request: AccountIDPasswordLoginRequest):
        response = await api_client.post("authenticate/login/password/account_id", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_name(api_client: ApiClient, login_request: NamePasswordLoginRequest):
        response = await api_client.post("authenticate/login/password/name", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_email(api_client: ApiClient, login_request: EmailPasswordLoginRequest):
        response = await api_client.post("authenticate/login/password/email", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_email_otp(api_client: ApiClient, email: str):
        await api_client.post("authenticate/login/email/otp", json={"email": email})

    @staticmethod
    async def verify_email_otp(api_client: ApiClient, email: str, code: str):
        response = await api_client.post("authenticate/login/email/otp/verify", json={"email": email, "code": code})
        return LoginResponse.model_validate(response)
