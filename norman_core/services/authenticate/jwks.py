from norman_objects.shared.authorization.jwks import JWKS
from norman_utils_external.singleton import Singleton

from norman_core.clients.http_client import HttpClient


class JWKS(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_jwks(self) -> JWKS:
        response = await self._http_client.get("authenticate/jwks/get")
        return JWKS.model_validate(response)
