from norman_objects.services.file_pull.download.tracked_download_union import TrackedDownloadUnion
from norman_objects.services.file_pull.requests.asset_download_request import AssetDownloadRequest
from norman_objects.services.file_pull.requests.input_download_request import InputDownloadRequest
from norman_objects.services.file_pull.requests.output_download_request import OutputDownloadRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class FilePull(metaclass=Singleton):
    """
    Provides coroutine-based methods for managing file downloads and uploads
    within the Norman platform.

    The `FilePull` class handles the submission and retrieval of download
    metadata and upload links for model-related files such as inputs, outputs,
    and assets.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_download_metadata(
        self,
        token: Sensitive[str],
        entity_id: str
    ) -> TrackedDownloadUnion:
        """
        **Coroutine**

        Retrieve metadata for a specific file download operation.

        This method returns download tracking details for inputs, outputs, or
        assets associated with the provided entity ID.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***entity_id*** (`str`) —
          The unique identifier of the entity (input, output, or asset)
          whose download metadata should be retrieved.

        **Response Structure**

        - ***response*** (`TrackedDownloadUnion`) —
          Union type containing metadata for tracked downloads.
          Includes file size, creation time, type, and download URLs.

        **Example Usage:**
        ```python
        file_pull_service = FilePull()
        metadata = await file_pull_service.get_download_metadata(token=my_token, entity_id="1234abcd")
        print("Download URL:", metadata.url)
        print("File type:", metadata.type)
        ```
        """
        response = await self._http_client.get(f"file-pull/metadata/{entity_id}", token)
        return TypeAdapter(TrackedDownloadUnion).validate_python(response)

    async def submit_asset_links(
        self,
        token: Sensitive[str],
        download_request: AssetDownloadRequest
    ) -> list[str]:
        """
        **Coroutine**

        Submit a request to upload or register asset file links for a model.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***download_request*** (`AssetDownloadRequest`) —
          Request object defining asset upload metadata.

          **Fields:**
          - **model_id** (`str`) — ID of the model whose assets are being uploaded.
          - **asset_links** (`List[str]`) — URLs or paths to the asset files.
          - **description** (`Optional[str]`) — Optional human-readable label.

        **Response Structure**

        - ***response*** (`List[str]`) —
          List of successfully registered asset link URLs.

        **Example Usage:**
        ```python
        request = AssetDownloadRequest(model_id="model_123", asset_links=["s3://bucket/weights.pt"])
        file_pull_service = FilePull()
        links = await file_pull_service.submit_asset_links(token=my_token, download_request=request)
        print("Registered asset links:", links)
        ```
        """
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/assets", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    async def submit_input_links(
        self,
        token: Sensitive[str],
        download_request: InputDownloadRequest
    ) -> list[str]:
        """
        **Coroutine**

        Submit input file links for processing or association with an invocation.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***download_request*** (`InputDownloadRequest`) —
          Request object defining model input upload details.

          **Fields:**
          - **invocation_id** (`str`) — ID of the invocation the inputs belong to.
          - **input_links** (`List[str]`) — Paths or URLs of input files.
          - **metadata** (`Optional[dict]`) — Optional additional input metadata.

        **Response Structure**

        - ***response*** (`List[str]`) —
          List of input upload URLs or references created by the system.

        **Example Usage:**
        ```python
        request = InputDownloadRequest(invocation_id="inv_456", input_links=["/tmp/input.png"])
        links = await FilePull().submit_input_links(token=my_token, download_request=request)
        print("Uploaded input links:", links)
        ```
        """
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/inputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)

    async def submit_output_links(
        self,
        token: Sensitive[str],
        download_request: OutputDownloadRequest
    ) -> list[str]:
        """
        **Coroutine**

        Submit output file links for an invocation or job.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***download_request*** (`OutputDownloadRequest`) —
          Request object containing model output details.

          **Fields:**
          - **invocation_id** (`str`) — ID of the invocation whose outputs are being uploaded.
          - **output_links** (`List[str]`) — URLs or file paths to the output artifacts.
          - **metadata** (`Optional[dict]`) — Optional output-specific metadata.

        **Response Structure**

        - ***response*** (`List[str]`) —
          List of uploaded or registered output link URLs.

        **Example Usage:**
        ```python
        request = OutputDownloadRequest(invocation_id="inv_789", output_links=["/tmp/output.png"])
        links = await FilePull().submit_output_links(token=my_token, download_request=request)
        print("Uploaded output links:", links)
        ```
        """
        json = download_request.model_dump(mode="json")
        response = await self._http_client.post("file-pull/upload/outputs", token, json=json)
        return TypeAdapter(list[str]).validate_python(response)
