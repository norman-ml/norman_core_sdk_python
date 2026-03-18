from norman_objects.shared.authorization.jwks import Jwks
from norman_utils.singleton import Singleton

from norman_core.clients.http_client import HttpClient


class JWKS(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_key_set(self) -> Jwks:
        response = await self._http_client.get("authenticate/jwks/get")
        return Jwks.model_validate(response)
