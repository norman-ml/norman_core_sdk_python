from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_asset_pairing_request import SocketAssetPairingRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_objects.shared.security.sensitive import Sensitive

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class FilePush(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def allocate_socket_for_asset(self, token: Sensitive[str], pairing_request: SocketAssetPairingRequest) -> SocketPairingResponse:
        json = pairing_request.model_dump(mode="json")
        response = await self._http_client.post("file-push/socket/pair/asset", token, json=json)
        return SocketPairingResponse.model_validate(response)

    async def allocate_socket_for_input(self, token: Sensitive[str], pairing_request: SocketInputPairingRequest) -> SocketPairingResponse:
        json = pairing_request.model_dump(mode="json")
        response = await self._http_client.post("file-push/socket/pair/input", token, json=json)
        return SocketPairingResponse.model_validate(response)

    async def complete_file_transfer(self, token: Sensitive[str], checksum_request: ChecksumRequest) -> None:
        json = checksum_request.model_dump(mode="json")
        await self._http_client.post("file-push/socket/complete", token, json=json)
