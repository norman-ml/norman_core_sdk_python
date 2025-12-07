from norman_objects.services.authenticate.register.register_auth_factor_request import RegisterAuthFactorRequest
from norman_objects.services.authenticate.register.register_email_request import RegisterEmailRequest
from norman_objects.services.authenticate.register.register_password_request import RegisterPasswordRequest
from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.shared.authentication.account_authentication_factors import AccountAuthenticationFactors
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

    **Constructor**

    ***__init__()***

    Initializes the Register service and creates an internal `HttpClient`
    instance used to communicate with the Norman authentication backend.
    Because this class is implemented as a singleton, the same HTTP client
    instance is reused across the application, improving connection reuse
    and reducing overhead.

    **Methods**
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

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***account_id*** (`str`) -
          Unique identifier of the account whose authentication factors should be retrieved.

        **Returns**

        - ***response*** (`AccountAuthenticationMethods`) -
          Object describing which authentication factors (email, password, key, etc.) are registered for the account.
        """
        response = await self._http_client.get(
            f"authenticate/register/get/authentication/factors/{account_id}", token
        )
        return AccountAuthenticationMethods.model_validate(response)
    async def get_authentication_factors(self, token: Sensitive[str], account_id: str) -> AccountAuthenticationFactors:
        response = await self._http_client.get(f"authenticate/register/get/authentication/factors/{account_id}", token)
        return AccountAuthenticationFactors.model_validate(response)

    async def generate_api_key(
        self,
        token: Sensitive[str],
        register_key_request: RegisterAuthFactorRequest
    ) -> str:
        """
        **Coroutine**

        Generate a new API key for an existing account.

        **Parameters**

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***register_key_request*** (`RegisterAuthFactorRequest`) -
          Request object specifying the account and key-generation parameters.

        **Returns**

        - ***response*** (`str`) -
          Newly generated API key as a sensitive string value.

        > ⚠️ **Important:**
        > Store the API key securely.
        > Keys **cannot be regenerated** - losing it requires creating a new one.
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

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***register_password_request*** (`RegisterPasswordRequest`) -
          Request object containing the password registration payload.

        **Returns**

        - ***response*** (`None`) -
          No response body. A successful status indicates password registration succeeded.
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

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***register_email_request*** (`RegisterEmailRequest`) -
          Request object containing the email registration details.

        **Returns**

        - ***response*** (`None`) -
          No response body. An email verification code is sent to the provided address.
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

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***email*** (`str`) -
          Email address that received the verification code.

        - ***code*** (`str`) -
          The one-time verification code sent to the user’s email.

        **Returns**

        - ***response*** (`None`) -
          No response body. Successful completion verifies the email.
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

        - ***token*** (`Sensitive[str]`) -
          Authentication token authorizing the request.

        - ***resend_email_verification_code_request*** (`ResendEmailVerificationCodeRequest`) -
          Request payload containing the target email and account ID.

        **Returns**

        - ***response*** (`None`) -
          No response body. A new OTP is delivered to the provided email.
        """
        json = resend_email_verification_code_request.model_dump(mode="json")
        await self._http_client.post("authenticate/register/email/resend/otp", token, json=json)
