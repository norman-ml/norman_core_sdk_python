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

          **Fields:**
          - **model_id** (`str`) — ID of the model associated with the asset.
          - **asset_name** (`str`) — Logical name of the asset (e.g., `"weights"`).
          - **size_bytes** (`int`) — Size of the asset in bytes.
          - **checksum** (`Optional[str]`) — Optional precomputed checksum for validation.

        **Response Structure**

        - ***response*** (`SocketPairingResponse`) —
          Contains information about the allocated socket for uploading.

          **Fields:**
          - **socket_url** (`str`) — WebSocket endpoint for file upload.
          - **upload_id** (`str`) — Unique identifier for the upload session.
          - **expires_at** (`datetime`) — Expiration time for the allocated socket.

        **Example Usage:**
        ```python
        request = SocketAssetPairingRequest(
            model_id="model_123",
            asset_name="weights",
            size_bytes=102400
        )
        file_push_service = FilePush()
        socket_info = await file_push_service.allocate_socket_for_asset(token=my_token, pairing_request=request)
        print("Upload via socket:", socket_info.socket_url)
        ```
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

          **Fields:**
          - **invocation_id** (`str`) — ID of the invocation associated with the input.
          - **input_name** (`str`) — Logical name of the input parameter.
          - **size_bytes** (`int`) — Size of the input file in bytes.
          - **checksum** (`Optional[str]`) — Optional checksum for data integrity verification.

        **Response Structure**

        - ***response*** (`SocketPairingResponse`) —
          Contains details about the allocated socket for uploading input data.

          **Fields:**
          - **socket_url** (`str`) — WebSocket endpoint for upload.
          - **upload_id** (`str`) — Identifier for the upload session.
          - **expires_at** (`datetime`) — Expiration timestamp for the socket allocation.

        **Example Usage:**
        ```python
        request = SocketInputPairingRequest(
            invocation_id="inv_789",
            input_name="image",
            size_bytes=204800
        )
        file_push_service = FilePush()
        socket_info = await file_push_service.allocate_socket_for_input(token=my_token, pairing_request=request)
        print("Input socket allocated:", socket_info.socket_url)
        ```
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

          **Fields:**
          - **upload_id** (`str`) — The upload session identifier.
          - **checksum** (`str`) — Hash value used to verify upload integrity (e.g., SHA256).
          - **size_bytes** (`int`) — File size in bytes for verification.
          - **completed_at** (`datetime`) — Timestamp when the upload was completed.

        **Response Structure**

        - ***response*** (`None`) —
          No response body. A successful status confirms the upload has been finalized and validated.

        **Example Usage:**
        ```python
        checksum_req = ChecksumRequest(
            upload_id="upl_456",
            checksum="abcd1234...",
            size_bytes=102400
        )
        await FilePush().complete_file_transfer(token=my_token, checksum_request=checksum_req)
        print("File transfer completed and verified.")
        ```
        """
        json = checksum_request.model_dump(mode="json")
        await self._http_client.post("file-push/socket/complete", token, json=json)
