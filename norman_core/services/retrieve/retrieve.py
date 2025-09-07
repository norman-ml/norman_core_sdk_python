from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import ApiClient, ResponseEncoding


class Retrieve:
    @staticmethod
    async def get_model_asset(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, asset_id: str):
        file_data = await api_client.get(
            f"retrieve/asset/{account_id}/{model_id}/{asset_id}",
            token,
            response_encoding=ResponseEncoding.Bytes
        )
        return file_data

    @staticmethod
    async def get_invocation_input(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, input_id: str):
        file_data = await api_client.get(
            f"retrieve/input/{account_id}/{model_id}/{invocation_id}/{input_id}",
            token,
            response_encoding=ResponseEncoding.Bytes
        )
        return file_data

    @staticmethod
    async def get_invocation_output(api_client: ApiClient, token: Sensitive[str], account_id: str, model_id: str, invocation_id: str, output_id: str):
        file_data = await api_client.get(
            f"retrieve/output/{account_id}/{model_id}/{invocation_id}/{output_id}",
            token,
            response_encoding=ResponseEncoding.Bytes
        )
        return file_data
