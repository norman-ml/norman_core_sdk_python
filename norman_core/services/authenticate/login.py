from norman_objects.services.authenticate.login.account_id_password_login_request import AccountIDPasswordLoginRequest
from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest
from norman_objects.services.authenticate.login.email_password_login_request import EmailPasswordLoginRequest
from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest
from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Login(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()
    # ==================== Get Authentication Factors (NEW) ====================

    async def get_authentication_factors_by_id(self, account_id: str) -> AccountAuthenticationMethods:
        response = await self._http_client.post(f"authenticate/login/get/authentication/factors/by-id/{account_id}")
        return AccountAuthenticationMethods.model_validate(response)

    async def get_authentication_factors_by_name(self, account_name: str) -> AccountAuthenticationMethods:
        response = await self._http_client.post(f"authenticate/login/get/authentication/factors/by-name/{account_name}")
        return AccountAuthenticationMethods.model_validate(response)

    async def get_authentication_factors_by_email(self, email: str) -> AccountAuthenticationMethods:
        response = await self._http_client.post(f"authenticate/login/get/authentication/factors/by-email/{email}")
        return AccountAuthenticationMethods.model_validate(response)


    async def login_default(self, account_id: str) -> LoginResponse:
        response = await self._http_client.post(f"authenticate/login/default/{account_id}")
        return LoginResponse.model_validate(response)

    async def login_with_key(self, api_key_login_request: ApiKeyLoginRequest) -> LoginResponse:
        json = api_key_login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/key", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_account_id(self, login_request: AccountIDPasswordLoginRequest) -> LoginResponse:
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/account_id", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_name(self, login_request: NamePasswordLoginRequest) -> LoginResponse:
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/name", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_email(self, login_request: EmailPasswordLoginRequest) -> LoginResponse:
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/email", json=json)
        return LoginResponse.model_validate(response)

    async def login_email_otp(self, email: str) -> None:
        await self._http_client.post("authenticate/login/email/otp", json={"email": email})

    async def verify_email_otp(self, email: str, code: str) -> LoginResponse:
        json = {"email": email, "code": code}
        response = await self._http_client.post("authenticate/login/email/otp/verify", json=json)
        return LoginResponse.model_validate(response)
