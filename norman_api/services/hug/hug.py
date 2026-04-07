from norman_objects.services.hug.huggingface_download_request import HuggingFaceDownloadRequest
from norman_objects.services.hug.tracked_huggingface_download import TrackedHuggingFaceDownload
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils.singleton import Singleton
from pydantic import TypeAdapter

from norman_api.clients.http_client import HttpClient


class Hug(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_download_metadata(self, token: Sensitive[str], entity_id: str) -> TrackedHuggingFaceDownload:
        response = await self._http_client.get(f"hug/metadata/{entity_id}", token)
        return TypeAdapter(TrackedHuggingFaceDownload).validate_python(response)

    async def download_huggingface_model(self, token: Sensitive[str], download_request: HuggingFaceDownloadRequest)  -> list[str]:
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("hug/download", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)