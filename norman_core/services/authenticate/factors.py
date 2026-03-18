from norman_core.clients.http_client import HttpClient
from norman_objects.shared.authentication.account_authentication_factors import AccountAuthenticationFactors
from norman_utils.singleton import Singleton


class Factors(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_authentication_factors_by_id(self, account_id: str) -> AccountAuthenticationFactors:
        response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-id/{account_id}")
        return AccountAuthenticationFactors.model_validate(response)

    async def get_authentication_factors_by_name(self, account_name: str) -> AccountAuthenticationFactors:
        response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-name/{account_name}")
        return AccountAuthenticationFactors.model_validate(response)

    async def get_authentication_factors_by_email(self, email: str) -> AccountAuthenticationFactors:
        response = await self._http_client.get(f"authenticate/login/get/authentication/factors/by-email/{email}")
        return AccountAuthenticationFactors.model_validate(response)
