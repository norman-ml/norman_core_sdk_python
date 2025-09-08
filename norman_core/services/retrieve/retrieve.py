from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import ApiClient, ResponseEncoding


class Retrieve:
    @staticmethod
    async def get_model_asset(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, asset_id: str):
        endpoint = f"retrieve/asset/{account_id}/{model_id}/{asset_id}"
        return await api_client.stream("GET", endpoint, token)

    @staticmethod
    async def get_invocation_input(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, input_id: str):
        endpoint = f"retrieve/input/{account_id}/{model_id}/{invocation_id}/{input_id}"
        return await api_client.stream("GET", endpoint, token)

    @staticmethod
    async def get_invocation_output(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, output_id: str):
        endpoint = f"retrieve/output/{account_id}/{model_id}/{invocation_id}/{output_id}"
        return await api_client.stream("GET", endpoint, token)