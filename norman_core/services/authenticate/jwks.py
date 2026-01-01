from norman_objects.shared.authorization.jwk import JWK
from norman_utils_external.singleton import Singleton

from norman_core.clients.http_client import HttpClient


class JWKS(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_jwks(self) -> list[JWK]:
        response = await self._http_client.get("authenticate/jwks/get")
        return [JWK.model_validate(key) for key in response["keys"]]
