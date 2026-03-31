from typing import Union, AsyncIterator
from pathlib import Path

import grpc
from xxhash import xxh3_64

from norman_api._app_config import AppConfig
from norman_core.services.file_push.proto.messages.assets import asset_identifiers_pb2
from norman_core.services.file_push.proto.messages.assets import asset_upload_request_pb2
from norman_core.services.file_push.proto.messages.inputs import input_identifiers_pb2
from norman_core.services.file_push.proto.messages.inputs import input_upload_request_pb2
from norman_core.services.file_push.proto.messages.shared import file_chunk_pb2
from norman_core.services.file_push.proto.messages.shared import upload_complete_pb2
from norman_core.services.file_push.proto.services import file_push_pb2_grpc


class GrpcClient:
    def __init__(self, server_address: str = None) -> None:
        if server_address is None:
            server_address = AppConfig.grpc.server_address
        self._server_address = server_address
        self._channel = None
        self._stub = None

    async def open(self) -> None:
        if self._channel is not None:
            return
        self._channel = grpc.aio.secure_channel(
            self._server_address,
            grpc.ssl_channel_credentials()
        )
        self._stub = file_push_pb2_grpc.FilePushStub(self._channel)

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def __aenter__(self) -> "GrpcClient":
        await self.open()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def upload_asset(self, token: str, account_id: str, model_id: str, version_id: str, asset_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None) -> None:
        if file_path is not None:
            path = Path(file_path)
            data_source = self._read_file(path)
        elif file_buffer is not None:
            data_source = self._read_buffer(file_buffer)
        else:
            raise ValueError("Provide either file_path or file_buffer")

        identifiers_msg = asset_upload_request_pb2.AssetUploadRequest(
            identifiers=asset_identifiers_pb2.AssetIdentifiers(
                account_id=account_id,
                model_id=model_id,
                version_id=version_id,
                asset_id=asset_id
            )
        )

        async def request_iterator():
            yield identifiers_msg

            hasher = xxh3_64()
            previous_chunk = None

            async for chunk in data_source:
                hasher.update(chunk)
                if previous_chunk is not None:
                    yield asset_upload_request_pb2.AssetUploadRequest(
                        chunk=file_chunk_pb2.FileChunk(data=previous_chunk)
                    )
                previous_chunk = chunk

            if previous_chunk is not None:
                yield asset_upload_request_pb2.AssetUploadRequest(
                    chunk=file_chunk_pb2.FileChunk(data=previous_chunk)
                )

            yield asset_upload_request_pb2.AssetUploadRequest(
                complete=upload_complete_pb2.UploadComplete(
                    client_checksum=hasher.hexdigest()
                )
            )

        call_metadata = [("authorization", f"Bearer {token}")]
        await self._stub.UploadAsset(
            request_iterator(),
            metadata=call_metadata
        )

    async def upload_input(self, token: str, account_id: str, model_id: str, version_id: str, invocation_id: str, input_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None) -> None:
        if file_path is not None:
            path = Path(file_path)
            data_source = self._read_file(path)
        elif file_buffer is not None:
            data_source = self._read_buffer(file_buffer)
        else:
            raise ValueError("Provide either file_path or file_buffer")

        identifiers_msg = input_upload_request_pb2.InputUploadRequest(
            identifiers=input_identifiers_pb2.InputIdentifiers(
                account_id=account_id,
                model_id=model_id,
                version_id=version_id,
                invocation_id=invocation_id,
                input_id=input_id
            )
        )

        async def request_iterator():
            yield identifiers_msg

            hasher = xxh3_64()
            previous_chunk = None

            async for chunk in data_source:
                hasher.update(chunk)
                if previous_chunk is not None:
                    yield input_upload_request_pb2.InputUploadRequest(
                        chunk=file_chunk_pb2.FileChunk(data=previous_chunk)
                    )
                previous_chunk = chunk

            if previous_chunk is not None:
                yield input_upload_request_pb2.InputUploadRequest(
                    chunk=file_chunk_pb2.FileChunk(data=previous_chunk)
                )

            yield input_upload_request_pb2.InputUploadRequest(
                complete=upload_complete_pb2.UploadComplete(
                    client_checksum=hasher.hexdigest()
                )
            )

        call_metadata = [("authorization", f"Bearer {token}")]
        await self._stub.UploadInput(
            request_iterator(),
            metadata=call_metadata
        )

    @staticmethod
    async def _read_file(path: Path) -> AsyncIterator[bytes]:
        import aiofiles
        async with aiofiles.open(path, mode="rb") as f:
            while True:
                chunk = await f.read(AppConfig.io.chunk_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    async def _read_buffer(buffer: bytes) -> AsyncIterator[bytes]:
        chunk_size = AppConfig.io.chunk_size
        offset = 0
        while offset < len(buffer):
            yield buffer[offset:offset + chunk_size]
            offset += chunk_size