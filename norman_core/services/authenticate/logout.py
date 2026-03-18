from norman_core.clients.http_client import HttpClient
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils.singleton import Singleton


class Logout(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def logout(self, token: Sensitive[str]) -> None:
        await self._http_client.post("authenticate/logout", token)
