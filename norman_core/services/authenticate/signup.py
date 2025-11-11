from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.signup.signup_email_request import SignupEmailRequest
from norman_objects.services.authenticate.signup.signup_key_request import SignupKeyRequest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_objects.shared.accounts.account import Account
from norman_utils_external.singleton import Singleton

from norman_core.clients.http_client import HttpClient


class Signup(metaclass=Singleton):
    """
    Provides coroutine-based methods for account registration
    and initial authentication within the Norman authentication system.

    The `Signup` class supports multiple registration flows including
    default signups, API key-based creation, email-based signup,
    and password-based signup.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def signup_default(self) -> LoginResponse:
        """
        **Coroutine**

        Create a default account and receive a `LoginResponse` for immediate authentication.

        This method is typically used for creating a temporary or anonymous
        account session.

        **Parameters**

        - *(none)* — This method does not require input parameters.

        **Response Structure**

        - ***response*** (`LoginResponse`) —
          The authenticated session returned after successful signup.

          **Fields:**
          - **token** (`str`) — Authentication token for the new session.
          - **account** (`Account`) — The newly created account metadata.
          - **expiration_time** (`datetime`) — Token expiration timestamp.

        **Example Usage:**
        ```python
        signup_service = Signup()
        response = await signup_service.signup_default()
        print("Created account:", response.account.id)
        print("Token:", response.token)
        ```
        """
        response = await self._http_client.put("authenticate/signup/default")
        return LoginResponse.model_validate(response)

    async def signup_and_generate_key(self, signup_request: SignupKeyRequest) -> Account:
        """
        **Coroutine**

        Register a new account and generate an API key for authentication.

        **Parameters**

        - ***signup_request*** (`SignupKeyRequest`) —
          Request object containing account details for key-based signup.

          **Fields:**
          - **name** (`str`) — Display name or identifier for the new account.
          - **description** (`Optional[str]`) — Optional description or label for the API key.
          - **expiration_time** (`Optional[datetime]`) — Optional expiration timestamp for the key.

        **Response Structure**

        - ***response*** (`Account`) —
          The created account metadata returned upon successful registration.

          **Fields:**
          - **id** (`str`) — Unique identifier for the account.
          - **creation_time** (`datetime`) — Account creation timestamp (UTC).
          - **name** (`str`) — Registered account display name.

        > ⚠️ **Important:**
        > Store the API key securely.
        > API keys **cannot be regenerated** — losing it requires creating a new one.

        **Example Usage:**
        ```python
        request = SignupKeyRequest(name="alice")
        account = await Signup().signup_and_generate_key(request)
        print("Account created:", account.name)
        ```
        """
        json = signup_request.model_dump(mode="json")
        response = await self._http_client.put("authenticate/signup/key", json=json)
        return response

    async def signup_with_password(self, signup_request: SignupPasswordRequest) -> Account:
        """
        **Coroutine**

        Register a new account using a username and password.

        **Parameters**

        - ***signup_request*** (`SignupPasswordRequest`) —
          Request object containing credentials for password-based signup.

          **Fields:**
          - **name** (`str`) — Desired username for the new account.
          - **password** (`str`) — Password for the account.
          - **email** (`Optional[str]`) — Optional email address to associate.

        **Response Structure**

        - ***response*** (`Account`) —
          The created account object returned upon successful signup.

          **Fields:**
          - **id** (`str`) — Unique account identifier.
          - **creation_time** (`datetime`) — Account creation timestamp.
          - **name** (`str`) — Registered username.

        **Example Usage:**
        ```python
        request = SignupPasswordRequest(name="alice", password="S3curePass!")
        account = await Signup().signup_with_password(request)
        print("Created account:", account.id)
        ```
        """
        json = signup_request.model_dump(mode="json")
        response = await self._http_client.put("authenticate/signup/password", json=json)
        return Account.model_validate(response)

    async def signup_with_email(self, signup_request: SignupEmailRequest) -> Account:
        """
        **Coroutine**

        Register a new account using an email-based signup flow.

        **Parameters**

        - ***signup_request*** (`SignupEmailRequest`) —
          Request object containing the email and optional display name.

          **Fields:**
          - **email** (`str`) — The email address to register.
          - **name** (`Optional[str]`) — Optional display name associated with the email.
          - **send_verification** (`Optional[bool]`) — Whether to send a verification email immediately.

        **Response Structure**

        - ***response*** (`Account`) —
          The created account metadata returned upon signup.

          **Fields:**
          - **id** (`str`) — Unique account identifier.
          - **creation_time** (`datetime`) — Account creation timestamp.
          - **name** (`str`) — Account display name.
          - **email** (`str`) — Registered email address.

        **Example Usage:**
        ```python
        request = SignupEmailRequest(email="user@example.com", name="User One")
        account = await Signup().signup_with_email(request)
        print("Email signup complete:", account.email)
        ```
        """
        json = signup_request.model_dump(mode="json")
        response = await self._http_client.put("authenticate/signup/email", json=json)
        return Account.model_validate(response)
