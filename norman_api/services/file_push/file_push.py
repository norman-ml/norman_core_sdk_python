from typing import Union
from pathlib import Path

from norman_objects.shared.security.sensitive import Sensitive

from norman_utils_external.singleton import Singleton
from norman_core.clients.grpc_client import GrpcClient


class FilePush(metaclass=Singleton):
    def __init__(self) -> None:
        self._grpc_client = GrpcClient()

    async def upload_asset(self, token: Sensitive[str], account_id: str, model_id: str, version_id: str, asset_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None, file_size: int = None) -> None:
        await self._grpc_client.open()
        response = await self._grpc_client.upload_asset(
            token=token.value(),
            account_id=account_id,
            model_id=model_id,
            version_id=version_id,
            asset_id=asset_id,
            file_path=file_path,
            file_buffer=file_buffer,
            file_size=file_size
        )
        if not response.success:
            raise RuntimeError(f"Asset upload failed: {response.message}")

    async def upload_input(self, token: Sensitive[str], account_id: str, model_id: str, version_id: str, invocation_id: str, input_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None, file_size: int = None) -> None:
        await self._grpc_client.open()
        response = await self._grpc_client.upload_input(
            token=token.value(),
            account_id=account_id,
            model_id=model_id,
            version_id=version_id,
            invocation_id=invocation_id,
            input_id=input_id,
            file_path=file_path,
            file_buffer=file_buffer,
            file_size=file_size
        )
        if not response.success:
            raise RuntimeError(f"Input upload failed: {response.message}")