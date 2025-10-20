from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.signup.signup_email_request import SignupEmailRequest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_objects.shared.accounts.account import Account

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Signup(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def signup_default(self):
        response = await self._http_client.put("authenticate/signup/default")
        return LoginResponse.model_validate(response)

    async def signup_with_password(self, signup_request: SignupPasswordRequest):
        response = await self._http_client.put(
            "authenticate/signup/password",
            json=signup_request.model_dump(mode="json"),
        )
        return Account.model_validate(response)

    async def signup_with_email(self, signup_request: SignupEmailRequest):
        response = await self._http_client.put(
            "authenticate/signup/email",
            json=signup_request.model_dump(mode="json"),
        )
        return Account.model_validate(response)
