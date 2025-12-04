from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_asset_pairing_request import SocketAssetPairingRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_objects.shared.security.sensitive import Sensitive

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class FilePush(metaclass=Singleton):
    """
    Provides coroutine-based methods for managing file upload operations
    in the Norman platform.

    The `FilePush` class handles socket allocation for uploading model
    assets and inputs, as well as completion tracking via checksum verification.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def allocate_socket_for_asset(
        self,
        token: Sensitive[str],
        pairing_request: SocketAssetPairingRequest
    ) -> SocketPairingResponse:
        """
        **Coroutine**

        Allocate a socket endpoint for uploading a model asset to Norman.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***pairing_request*** (`SocketAssetPairingRequest`) —
          Request object defining asset pairing and upload configuration.

        **Response Structure**

        - ***response*** (`SocketPairingResponse`) —
          Contains information about the allocated socket for uploading.
        """
        json = pairing_request.model_dump(mode="json")
        response = await self._http_client.post("file-push/socket/pair/asset", token, json=json)
        return SocketPairingResponse.model_validate(response)

    async def allocate_socket_for_input(
        self,
        token: Sensitive[str],
        pairing_request: SocketInputPairingRequest
    ) -> SocketPairingResponse:
        """
        **Coroutine**

        Allocate a socket endpoint for uploading model input data to Norman.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***pairing_request*** (`SocketInputPairingRequest`) —
          Request object defining the input upload configuration.

        **Response Structure**

        - ***response*** (`SocketPairingResponse`) —
          Contains details about the allocated socket for uploading input data.
        """
        json = pairing_request.model_dump(mode="json")
        response = await self._http_client.post("file-push/socket/pair/input", token, json=json)
        return SocketPairingResponse.model_validate(response)

    async def complete_file_transfer(
        self,
        token: Sensitive[str],
        checksum_request: ChecksumRequest
    ) -> None:
        """
        **Coroutine**

        Notify Norman that a file upload has completed and verify its integrity.

        This finalizes the upload session by submitting a checksum for validation.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***checksum_request*** (`ChecksumRequest`) —
          Request object containing checksum validation details.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. A successful status confirms the upload has been finalized and validated.
        """
        json = checksum_request.model_dump(mode="json")
        await self._http_client.post("file-push/socket/complete", token, json=json)
