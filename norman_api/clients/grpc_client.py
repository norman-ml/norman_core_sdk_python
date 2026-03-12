from typing import Union, AsyncIterator
from pathlib import Path

import grpc
from xxhash import xxh3_64

from norman_core._app_config import AppConfig
from norman_core.services.file_push.proto import file_push_pb2, file_push_pb2_grpc


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
        self._stub = file_push_pb2_grpc.FilePushServiceStub(self._channel)

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

    async def upload_asset(self, token: str, account_id: str, model_id: str, version_id: str, asset_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None, file_size: int = None) -> file_push_pb2.UploadStatus:
        if file_path is not None:
            path = Path(file_path)
            file_size = path.stat().st_size
            data_source = self._read_file(path)
        elif file_buffer is not None:
            if file_size is None:
                file_size = len(file_buffer)
            data_source = self._read_buffer(file_buffer)
        else:
            raise ValueError("Provide either file_path or file_buffer")

        metadata_msg = file_push_pb2.AssetUploadRequest(
            metadata=file_push_pb2.AssetMetadata(
                account_id=account_id,
                model_id=model_id,
                version_id=version_id,
                asset_id=asset_id,
                file_size_in_bytes=file_size
            )
        )

        async def request_iterator():
            yield metadata_msg

            hasher = xxh3_64()
            previous_chunk = None

            async for chunk in data_source:
                hasher.update(chunk)
                if previous_chunk is not None:
                    yield file_push_pb2.AssetUploadRequest(
                        chunk=file_push_pb2.FileChunk(data=previous_chunk)
                    )
                previous_chunk = chunk

            if previous_chunk is not None:
                yield file_push_pb2.AssetUploadRequest(
                    chunk=file_push_pb2.FileChunk(
                        data=previous_chunk,
                        checksum=hasher.hexdigest()
                    )
                )

        call_metadata = [("authorization", f"Bearer {token}")]
        response = await self._stub.UploadAsset(
            request_iterator(),
            metadata=call_metadata
        )
        return response

    async def upload_input(self, token: str, account_id: str, model_id: str, version_id: str, invocation_id: str, input_id: str, file_path: Union[str, Path] = None, file_buffer: bytes = None, file_size: int = None) -> file_push_pb2.UploadStatus:
        if file_path is not None:
            path = Path(file_path)
            file_size = path.stat().st_size
            data_source = self._read_file(path)
        elif file_buffer is not None:
            if file_size is None:
                file_size = len(file_buffer)
            data_source = self._read_buffer(file_buffer)
        else:
            raise ValueError("Provide either file_path or file_buffer")

        metadata_msg = file_push_pb2.InputUploadRequest(
            metadata=file_push_pb2.InputMetadata(
                account_id=account_id,
                model_id=model_id,
                version_id=version_id,
                invocation_id=invocation_id,
                input_id=input_id,
                file_size_in_bytes=file_size
            )
        )

        async def request_iterator():
            yield metadata_msg

            hasher = xxh3_64()
            previous_chunk = None

            async for chunk in data_source:
                hasher.update(chunk)
                if previous_chunk is not None:
                    yield file_push_pb2.InputUploadRequest(
                        chunk=file_push_pb2.FileChunk(data=previous_chunk)
                    )
                previous_chunk = chunk

            if previous_chunk is not None:
                yield file_push_pb2.InputUploadRequest(
                    chunk=file_push_pb2.FileChunk(
                        data=previous_chunk,
                        checksum=hasher.hexdigest()
                    )
                )

        call_metadata = [("authorization", f"Bearer {token}")]
        response = await self._stub.UploadInput(
            request_iterator(),
            metadata=call_metadata
        )
        return response

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