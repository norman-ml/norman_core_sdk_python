from norman_objects.services.file_pull.download.tracked_download import TrackedDownload
from norman_objects.services.file_pull.requests.asset_download_request import AssetDownloadRequest
from norman_objects.services.file_pull.requests.input_download_request import InputDownloadRequest
from norman_objects.services.file_pull.requests.output_download_request import OutputDownloadRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class FilePull:
    @staticmethod
    async def get_download_metadata(api_client: ApiClient, token: Sensitive[str], entity_id: str):
        response = await api_client.get(f"file-pull/metadata/{entity_id}", token)
        return TrackedDownload.model_validate(response)

    @staticmethod
    async def submit_asset_links(api_client: ApiClient, token: Sensitive[str], download_request: AssetDownloadRequest):
        json = download_request.model_dump(mode="json")

        response = await api_client.post("file-pull/upload/assets", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    @staticmethod
    async def submit_input_links(api_client: ApiClient, token: Sensitive[str], download_request: InputDownloadRequest):
        json = download_request.model_dump(mode="json")

        response = await api_client.post("file-pull/upload/inputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    @staticmethod
    async def submit_output_links(api_client: ApiClient, token: Sensitive[str], download_request: OutputDownloadRequest):
        json = download_request.model_dump(mode="json")

        response = await api_client.post("file-pull/upload/outputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)
