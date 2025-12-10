from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods


async def get_authentication_factors_by_id(self, account_id: str) -> AccountAuthenticationMethods:
    response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-id/{account_id}")
    return AccountAuthenticationMethods.model_validate(response)

async def get_authentication_factors_by_name(self, account_name: str) -> AccountAuthenticationMethods:
    response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-name/{account_name}")
    return AccountAuthenticationMethods.model_validate(response)

async def get_authentication_factors_by_email(self, email: str) -> AccountAuthenticationMethods:
    response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-email/{email}")
    return AccountAuthenticationMethods.model_validate(response)
