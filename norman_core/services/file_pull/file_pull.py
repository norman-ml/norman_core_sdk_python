from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import ApiClient


class FilePull:
    @staticmethod
    async def get_download_metadata(api_client: ApiClient, token: Sensitive[str], entity_id: str):
        response = await api_client.get(f"file-pull/metadata/{entity_id}", token)
        return response

    @staticmethod
    async def submit_asset_links(api_client: ApiClient, token: Sensitive[str], download_request: AssetDownloadRequest):
        response = await api_client.post("file-pull/upload/assets", token, json=download_request.model_dump(mode="json"))
        return response

    @staticmethod
    async def submit_input_links(api_client: ApiClient, token: Sensitive[str], download_request: InputDownloadRequest):
        response = await api_client.post("file-pull/upload/inputs", token, json=download_request.model_dump(mode="json"))
        return response

    @staticmethod
    async def submit_output_links(api_client: ApiClient, token: Sensitive[str], download_request: OutputDownloadRequest):
        response = await api_client.post("file-pull/upload/outputs", token, json=download_request.model_dump(mode="json"))
        return response