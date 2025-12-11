from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_objects.services.hug.huggingface_download_request import HuggingFaceDownloadRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Hug(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def download_huggingface_model(self, token: Sensitive[str], huggingface_download_request: HuggingFaceDownloadRequest)  -> list[str]:
        json = huggingface_download_request.model_dump(mode="json")
        await self._http_client.post("hug/download", token, json=json)
