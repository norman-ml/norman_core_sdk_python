from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton

from norman_core.clients.http_client import HttpClient, ResponseEncoding


class Retrieve(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_model_asset(self, token: Sensitive[str], account_id: str, model_id: str, asset_id: str):
        endpoint = f"retrieve/asset/{account_id}/{model_id}/{asset_id}"
        return await self._http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)

    async def get_invocation_input(self, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, input_id: str):
        endpoint = f"retrieve/input/{account_id}/{model_id}/{invocation_id}/{input_id}"
        return await self._http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)

    async def get_invocation_output(self, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, output_id: str):
        endpoint = f"retrieve/output/{account_id}/{model_id}/{invocation_id}/{output_id}"
        return await self._http_client.get(endpoint, token, response_encoding=ResponseEncoding.Iterator)
