from norman_objects.services.authenticate.login.account_id_password_login_request import AccountIDPasswordLoginRequest
from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest
from norman_objects.services.authenticate.login.email_password_login_request import EmailPasswordLoginRequest
from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Login(metaclass=Singleton):
    """
    Provides coroutine-based login operations for the Norman authentication system.

    The `Login` class supports multiple authentication flows, including
    API key login, password-based login (by ID, name, or email),
    and email-based one-time password (OTP) verification.

    Each method communicates with the `authenticate/login` endpoints
    using the internal HTTP client.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def login_default(self, account_id: str) -> LoginResponse:
        """
        **Coroutine**

        Perform a default login for a specific account ID. works only for account without any auth factors.

        **Parameters**

        - ***account_id*** (`str`) —
          The unique identifier of the account to log into.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          The authenticated session object, containing token and account details.
        """
        response = await self._http_client.post(f"authenticate/login/default/{account_id}")
        return LoginResponse.model_validate(response)

    async def login_with_key(self, api_key_login_request: ApiKeyLoginRequest) -> LoginResponse:
        """
        **Coroutine**

        Authenticate using an API key.

        **Parameters**

        - ***api_key_login_request*** (`ApiKeyLoginRequest`) —
          Request object containing the API key credentials.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          The login response containing the authentication token and account metadata.
        """
        json = api_key_login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/key", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_account_id(self, login_request: AccountIDPasswordLoginRequest) -> LoginResponse:
        """
        **Coroutine**

        Authenticate with an account ID and password.

        **Parameters**

        - ***login_request*** (`AccountIDPasswordLoginRequest`) —
          Request object containing the account ID and password.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          Contains authentication token, session data, and account metadata.
        """
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/account_id", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_name(self, login_request: NamePasswordLoginRequest) -> LoginResponse:
        """
        **Coroutine**

        Authenticate with an account name and password.

        **Parameters**

        - ***login_request*** (`NamePasswordLoginRequest`) —
          Request object containing the account name and password.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          Login result including token, expiration, and account details.
        """
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/name", json=json)
        return LoginResponse.model_validate(response)

    async def login_password_email(self, login_request: EmailPasswordLoginRequest) -> LoginResponse:
        """
        **Coroutine**

        Authenticate with an email address and password.

        **Parameters**

        - ***login_request*** (`EmailPasswordLoginRequest`) —
          Request object containing the email and password.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          Contains token and authenticated account details.
        """
        json = login_request.model_dump(mode="json")
        response = await self._http_client.post("authenticate/login/password/email", json=json)
        return LoginResponse.model_validate(response)

    async def login_email_otp(self, email: str) -> None:
        """
        **Coroutine**

        Initiate an email-based One-Time Password (OTP) login flow.

        Sends an OTP code to the provided email address for verification.

        **Parameters**

        - ***email*** (`str`) —
          The user’s email address to which the OTP will be sent.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. A verification code is sent to the email.
        """
        await self._http_client.post("authenticate/login/email/otp", json={"email": email})

    async def verify_email_otp(self, email: str, code: str) -> LoginResponse:
        """
        **Coroutine**

        Verify a previously sent email OTP and complete the login process.

        **Parameters**

        - ***email*** (`str`) —
          The email address used during OTP initiation.

        - ***code*** (`str`) —
          The one-time password code received via email.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          Contains authentication token and account details upon successful verification.
        """
        json = {"email": email, "code": code}
        response = await self._http_client.post("authenticate/login/email/otp/verify", json=json)
        return LoginResponse.model_validate(response)
