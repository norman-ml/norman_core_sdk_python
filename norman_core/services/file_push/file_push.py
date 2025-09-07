import asyncio
import base64
import contextlib
from typing import AsyncGenerator

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
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
        authentication_header = base64.b64decode(socket_info.authentication_header)
        encryptor = FilePush._create_encryptor(socket_info)

        body_stream = StreamingUtils.chain_streams([authentication_header], file_stream)

        stream_reader, stream_writer = await asyncio.open_connection(socket_info.host, socket_info.port)
        try:
            async for chunk in body_stream:
                encrypted = encryptor.update(chunk)
                stream_writer.write(encrypted)
                if stream_writer.transport.get_write_buffer_size() >= AppConfig.io.flush_size:
                    await stream_writer.drain()
                await stream_writer.drain()
                yield chunk
        finally:
            stream_writer.close()
            with contextlib.suppress(ConnectionResetError):
                await stream_writer.wait_closed()

    @staticmethod
    def _create_encryptor(pairing_response: SocketPairingResponse):
        key_bytes = base64.b64decode(pairing_response.encryption_key)
        base_nonce12 = base64.b64decode(pairing_response.nonce)

        counter_nonce4 = (0).to_bytes(4, "little")
        full_nonce16 = counter_nonce4 + base_nonce12

        cypher =  Cipher(algorithms.ChaCha20(key_bytes, full_nonce16), mode=None)
        encryptor = cypher.encryptor()

        return encryptor
