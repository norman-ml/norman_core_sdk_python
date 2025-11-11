import asyncio
import base64
import contextlib
from typing import AsyncGenerator, Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_utils_external.streaming_utils import StreamingUtils, AsyncBufferedReader
from xxhash import xxh3_64

from norman_core._app_config import AppConfig


class SocketClient:
    """
    Provides low-level streaming and encryption utilities for file upload
    sockets within the Norman platform.

    The `SocketClient` handles encrypted binary streaming between the
    client and a Norman-managed upload socket. It is typically used by
    `FilePush` to send large assets or model files over an allocated
    WebSocket or TCP socket.
    """

    @staticmethod
    async def write_and_digest(
        socket_info: SocketPairingResponse,
        asset_stream: AsyncBufferedReader
    ) -> str:
        """
        **Coroutine**

        Write an asset stream to a paired socket while computing its hash digest.

        This method sends a binary stream (e.g., a model asset or input file)
        through an encrypted socket, and simultaneously computes its XXH3-64
        checksum for validation.

        **Parameters**

        - ***socket_info*** (`SocketPairingResponse`) —
          The socket pairing information returned from the `FilePush` API.
          Contains authentication headers, encryption keys, and socket details.

          **Key Fields:**
          - **host** (`str`) — Target socket hostname.
          - **port** (`int`) — Socket port number.
          - **encryption_key** (`str`) — Base64-encoded encryption key.
          - **nonce** (`str`) — Base64-encoded nonce used for ChaCha20 encryption.
          - **authentication_header** (`str`) — Base64-encoded header for request authentication.

        - ***asset_stream*** (`AsyncBufferedReader`) —
          Asynchronous stream reader providing the file or asset data to be uploaded.

        **Response Structure**

        - ***response*** (`str`) —
          Hexadecimal XXH3-64 hash digest of the uploaded file, used for checksum validation.

        **Example Usage:**
        ```python
        async with AsyncBufferedReader(open("weights.pt", "rb")) as stream:
            checksum = await SocketClient.write_and_digest(socket_info, stream)
            print("Asset checksum:", checksum)
        ```
        """
        hash_stream = xxh3_64()
        body_stream = StreamingUtils.process_read_stream(
            asset_stream, hash_stream.update, AppConfig.io.chunk_size, False
        )

        async for _ in SocketClient.write(socket_info, body_stream):
            ...

        return hash_stream.hexdigest()

    @staticmethod
    async def write(
        socket_info: SocketPairingResponse,
        file_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[bytes, None]:
        """
        **Coroutine**

        Write a stream of encrypted binary data to a paired socket.

        This method encrypts and transmits a binary stream to a socket endpoint
        using ChaCha20 encryption and flow-controlled async writes.

        **Parameters**

        - ***socket_info*** (`SocketPairingResponse`) —
          The socket pairing information returned from `FilePush`.

          **Key Fields:**
          - **host** (`str`) — Target socket hostname.
          - **port** (`int`) — Socket port number.
          - **encryption_key** (`str`) — Base64-encoded ChaCha20 encryption key.
          - **nonce** (`str`) — Base64-encoded nonce used for encryption.
          - **authentication_header** (`str`) — Base64-encoded header prepended to the stream.

        - ***file_stream*** (`AsyncGenerator[bytes, None]`) —
          Asynchronous generator yielding raw binary chunks to be written.

        **Response Structure**

        - ***response*** (`AsyncGenerator[bytes, None]`) —
          Asynchronous generator that yields the original unencrypted chunks
          after successful socket transmission.

        **Example Usage:**
        ```python
        async def file_gen():
            async for chunk in AsyncBufferedReader(open("file.bin", "rb")):
                yield chunk

        async for sent_chunk in SocketClient.write(socket_info, file_gen()):
            print(f"Sent {len(sent_chunk)} bytes...")
        ```
        """
        authentication_header = base64.b64decode(socket_info.authentication_header)
        encryptor = SocketClient._create_encryptor(socket_info)

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
    def _create_encryptor(pairing_response: SocketPairingResponse) -> Any:
        """
        **Static Method**

        Create and initialize a ChaCha20 encryptor from pairing metadata.

        This helper constructs a ChaCha20 encryption context using
        the encryption key and nonce provided in the pairing response.

        **Parameters**

        - ***pairing_response*** (`SocketPairingResponse`) —
          Pairing object containing `encryption_key` and `nonce` values.

        **Response Structure**

        - ***response*** (`cryptography.hazmat.primitives.ciphers.CipherContext`) —
          Active encryptor object used for data streaming.

        **Example Usage:**
        ```python
        encryptor = SocketClient._create_encryptor(socket_info)
        encrypted_block = encryptor.update(b"data chunk")
        ```
        """
        key_bytes = base64.b64decode(pairing_response.encryption_key)
        base_nonce12 = base64.b64decode(pairing_response.nonce)
        counter_nonce4 = (0).to_bytes(4, "little")
        full_nonce16 = counter_nonce4 + base_nonce12

        cipher = Cipher(algorithms.ChaCha20(key_bytes, full_nonce16), mode=None)
        encryptor = cipher.encryptor()
        return encryptor
