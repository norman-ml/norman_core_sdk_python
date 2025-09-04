from norman_objects.shared.accounts.account import Account

from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.signup.signup_email_request import SignupEmailRequest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_core.utils.api_client import ApiClient


class Signup:
    @staticmethod
    async def signup_default(api_client: ApiClient):
        response = await api_client.put("authenticate/signup/default")
        return LoginResponse.model_validate(response)

    @staticmethod
    async def signup_with_password(api_client: ApiClient, signup_request: SignupPasswordRequest):
        response = await api_client.put("authenticate/signup/password", json=signup_request.model_dump(mode="json"))
        return Account.model_validate(response)

    @staticmethod
    async def signup_with_email(api_client: ApiClient, signup_request: SignupEmailRequest):
        response = await api_client.put("authenticate/signup/email", json=signup_request.model_dump(mode="json"))
        return Account.model_validate(response)
