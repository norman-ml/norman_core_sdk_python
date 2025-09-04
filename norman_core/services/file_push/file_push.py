import asyncio
import base64
import contextlib
from typing import AsyncGenerator

from Crypto.Cipher import ChaCha20
from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_asset_pairing_request import SocketAssetPairingRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.streaming_utils import StreamingUtils

from norman_core._app_config import AppConfig
from norman_core.utils.api_client import ApiClient


class FilePush:
    @staticmethod
    async def allocate_socket_for_asset(api_client: ApiClient, token: Sensitive[str], pairing_request: SocketAssetPairingRequest):
        response = await api_client.post("file-push/socket/pair/asset", token, json=pairing_request.model_dump(mode="json"))
        return SocketPairingResponse.model_validate(response)

    @staticmethod
    async def allocate_socket_for_input(api_client: ApiClient, token: Sensitive[str], pairing_request: SocketInputPairingRequest):
        response = await api_client.post("file-push/socket/pair/input", token, json=pairing_request.model_dump(mode="json"))
        return SocketPairingResponse.model_validate(response)

    @staticmethod
    async def complete_file_transfer(api_client: ApiClient, token: Sensitive[str], checksum_request: ChecksumRequest):
        await api_client.post("file-push/socket/complete", token, json=checksum_request.model_dump(mode="json"))

    @staticmethod
    async def write_file(socket_info: SocketPairingResponse, file_stream: AsyncGenerator[bytes]):
        key_bytes = base64.b64decode(socket_info.encryption_key)
        authentication_header = base64.b64decode(socket_info.authentication_header)
        base_nonce12 = base64.b64decode(socket_info.nonce)

        cipher = ChaCha20.new(key=key_bytes, nonce=base_nonce12)

        body_stream = StreamingUtils.chain_streams([authentication_header], file_stream)

        _, client_socket = await asyncio.open_connection(socket_info.host, socket_info.port)
        try:
            async for chunk in body_stream:
                encrypted = cipher.encrypt(chunk)
                client_socket.write(encrypted)
                if client_socket.transport.get_write_buffer_size() >= AppConfig.io.flush_size:
                    await client_socket.drain()
                await client_socket.drain()
                yield chunk
        finally:
            client_socket.close()
            with contextlib.suppress(ConnectionResetError):
                await client_socket.wait_closed()
