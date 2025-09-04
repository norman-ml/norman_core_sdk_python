import asyncio

from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.services.authenticate.signup.signup_email_request import SignupEmailRequest

from norman_core import ApiClient
from norman_core.services.authenticate.login import Login
from norman_core.services.authenticate.register import Register
from norman_core.services.authenticate.signup import Signup


async def main():
    email = "avremyback@gmail.com"
    api_client = ApiClient(timeout=180)
    signup_email_request = SignupEmailRequest(
        email=email,
        name="AvremyEmail"
    )

    login_response  = await Login.login_default(api_client, "23845817539265909516248968151742234835")

    # account = await Signup.signup_with_email(api_client, signup_email_request)
    # print(f"Account ID: {account.id}")


    await Register.resend_email_otp(api_client, login_response.access_token, ResendEmailVerificationCodeRequest(
        email=email,
        account_id=login_response.account.id,
    ))

    # await Login.login_email_otp(api_client, email)
    otp = input("OTP:")

    login_response = await Register.verify_email(api_client, login_response.access_token, email, otp)
    print(login_response)



    await api_client.close()

asyncio.run(main())