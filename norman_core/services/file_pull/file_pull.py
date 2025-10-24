from norman_objects.services.file_pull.download.tracked_download_union import TrackedDownloadUnion
from norman_objects.services.file_pull.requests.asset_download_request import AssetDownloadRequest
from norman_objects.services.file_pull.requests.input_download_request import InputDownloadRequest
from norman_objects.services.file_pull.requests.output_download_request import OutputDownloadRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class FilePull(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_download_metadata(self, token: Sensitive[str], entity_id: str) -> TrackedDownloadUnion:
        response = await self._http_client.get(f"file-pull/metadata/{entity_id}", token)
        return TypeAdapter(TrackedDownloadUnion).validate_python(response)

    async def submit_asset_links(self, token: Sensitive[str], download_request: AssetDownloadRequest) -> list[str] :
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/assets", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    async def submit_input_links(self, token: Sensitive[str], download_request: InputDownloadRequest) -> list[str]:
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/inputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    async def submit_output_links(self, token: Sensitive[str], download_request: OutputDownloadRequest) -> list[str]:
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/outputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)
