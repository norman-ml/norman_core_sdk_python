from norman_objects.services.authenticate.register.register_auth_factor_request import RegisterAuthFactorRequest
from norman_objects.services.authenticate.register.register_email_request import RegisterEmailRequest
from norman_objects.services.authenticate.register.register_password_request import RegisterPasswordRequest
from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods
from norman_objects.shared.security.sensitive import Sensitive

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Register(metaclass=Singleton):
    """
    Provides coroutine-based registration and authentication-factor management
    for the Norman authentication service.

    The `Register` class handles registration flows including password creation,
    email registration and verification, API-key generation, and retrieval
    of available authentication factors.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_authentication_factors(
        self,
        token: Sensitive[str],
        account_id: str
    ) -> AccountAuthenticationMethods:
        """
        **Coroutine**

        Retrieve all authentication factors currently associated with a given account.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***account_id*** (`str`) —
          Unique identifier of the account whose authentication factors should be retrieved.

        **Response Structure**

        - ***response*** (`AccountAuthenticationMethods`) —
          Object describing which authentication factors (email, password, key, etc.) are registered for the account.

        **Example Usage:**
        ```python
        register_service = Register()
        factors = await register_service.get_authentication_factors(token=my_token, account_id="user_123")
        print(factors.available_methods)
        ```
        """
        response = await self._http_client.get(
            f"authenticate/register/get/authentication/factors/{account_id}", token
        )
        return AccountAuthenticationMethods.model_validate(response)

    async def generate_api_key(
        self,
        token: Sensitive[str],
        register_key_request: RegisterAuthFactorRequest
    ) -> str:
        """
        **Coroutine**

        Generate a new API key for an existing account.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***register_key_request*** (`RegisterAuthFactorRequest`) —
          Request object specifying the account and key-generation parameters.

          **Fields:**
          - **account_id** (`str`) — Account for which to generate the key.
          - **description** (`Optional[str]`) — Optional human-readable key label.
          - **expiration_time** (`Optional[datetime]`) — Optional expiration timestamp.

        **Response Structure**

        - ***response*** (`str`) —
          Newly generated API key as a sensitive string value.

        > ⚠️ **Important:**
        > Store the API key securely.
        > Keys **cannot be regenerated** — losing it requires creating a new one.

        **Example Usage:**
        ```python
        request = RegisterAuthFactorRequest(account_id="user_123", description="CI key")
        api_key = await Register().generate_api_key(token=my_token, register_key_request=request)
        print("Generated API key:", api_key)
        ```
        """
        json = register_key_request.model_dump(mode="json")
        api_key = await self._http_client.post("authenticate/generate/key", token, json=json)
        return api_key

    async def register_password(
        self,
        token: Sensitive[str],
        register_password_request: RegisterPasswordRequest
    ) -> None:
        """
        **Coroutine**

        Register or update a password authentication factor for an account.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***register_password_request*** (`RegisterPasswordRequest`) —
          Request object containing the password registration payload.

          **Fields:**
          - **account_id** (`str`) — Target account identifier.
          - **password** (`str`) — Desired password for the account.
          - **require_reset** (`Optional[bool]`) — If `True`, forces a reset on next login.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. A successful status indicates password registration succeeded.

        **Example Usage:**
        ```python
        req = RegisterPasswordRequest(account_id="user_123", password="My$ecurePass")
        await Register().register_password(token=my_token, register_password_request=req)
        print("Password set successfully.")
        ```
        """
        json = register_password_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/password", token, json=json)

    async def register_email(
        self,
        token: Sensitive[str],
        register_email_request: RegisterEmailRequest
    ) -> None:
        """
        **Coroutine**

        Register an email authentication factor for an account.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***register_email_request*** (`RegisterEmailRequest`) —
          Request object containing the email registration details.

          **Fields:**
          - **account_id** (`str`) — Target account identifier.
          - **email** (`str`) — Email address to associate with the account.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. An email verification code is sent to the provided address.

        **Example Usage:**
        ```python
        req = RegisterEmailRequest(account_id="user_123", email="user@example.com")
        await Register().register_email(token=my_token, register_email_request=req)
        print("Verification email sent.")
        ```
        """
        json = register_email_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/email", token, json=json)

    async def verify_email(
        self,
        token: Sensitive[str],
        email: str,
        code: str
    ) -> None:
        """
        **Coroutine**

        Verify an email authentication factor using a one-time code.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***email*** (`str`) —
          Email address that received the verification code.

        - ***code*** (`str`) —
          The one-time verification code sent to the user’s email.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. Successful completion verifies the email.

        **Example Usage:**
        ```python
        register_service = Register()
        await register_service.verify_email(token=my_token, email="user@example.com", code="123456")
        print("Email verified successfully.")
        ```
        """
        await self._http_client.post(f"authenticate/register/email/verify/{email}/{code}", token)

    async def resend_email_otp(
        self,
        token: Sensitive[str],
        resend_email_verification_code_request: ResendEmailVerificationCodeRequest
    ) -> None:
        """
        **Coroutine**

        Resend a verification code to the registered email address.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***resend_email_verification_code_request*** (`ResendEmailVerificationCodeRequest`) —
          Request payload containing the target email and account ID.

          **Fields:**
          - **account_id** (`str`) — Target account identifier.
          - **email** (`str`) — Email to which the OTP should be resent.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. A new OTP is delivered to the provided email.

        **Example Usage:**
        ```python
        req = ResendEmailVerificationCodeRequest(account_id="user_123", email="user@example.com")
        await Register().resend_email_otp(token=my_token, resend_email_verification_code_request=req)
        print("OTP resent to email.")
        ```
        """
        json = resend_email_verification_code_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/email/resend/otp", token, json=json)
