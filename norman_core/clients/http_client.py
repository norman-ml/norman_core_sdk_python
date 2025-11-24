from types import TracebackType
from typing import Any, AsyncGenerator, Optional, Type
from typing_extensions import Unpack

import httpx
from httpx import Response
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton

from norman_core._app_config import AppConfig
from norman_core.clients.objects.request_kwargs import RequestKwargs
from norman_core.clients.objects.response_encoding import ResponseEncoding


class HttpClient(metaclass=Singleton):
    """
    Asynchronous HTTP client wrapper used internally by Norman services.

    The `HttpClient` class provides coroutine-based convenience methods
    (`get`, `post`, `put`, `patch`, `delete`, `post_multipart`) that wrap
    an underlying `httpx.AsyncClient`. It supports automatic base URL
    resolution, timeout configuration, request header management, and
    multiple response decoding modes (`JSON`, `Bytes`, `Text`, `Iterator`).

    All requests use Bearer-token authorization with the `Sensitive[str]`
    security wrapper for secure credential handling.

    > ⚠️ **Important:**
    > Before making any API calls, you must **open** the client using `await client.open()`
    > and **close** it using `await client.close()` once done —
    > or simply use it as an **async context manager**:
    >
    > ```python
    > async with HttpClient() as client:
    >     response = await client.get("persist/models/get", token=my_token)
    >     print(response)
    > ```
    >
    > Using the context manager is the recommended pattern, as it ensures
    > proper session lifecycle management and automatic cleanup of resources.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None) -> None:
        """
        Initialize an asynchronous HTTP client.

        **Parameters**

        - ***base_url*** (`Optional[str]`) —
          Base URL for all requests. Defaults to the configured value in `AppConfig.http.base_url`.

        - ***timeout*** (`Optional[float]`) —
          Request timeout in seconds. Defaults to `AppConfig.http.timeout_seconds`.

        The client automatically manages persistent connections using
        an internal reentrance counter to safely reuse sessions.
        """
        self._client = None
        self._reentrance_count = 0

        self._base_url = base_url or AppConfig.http.base_url
        self._timeout = timeout or AppConfig.http.timeout_seconds

        self._headers = {"Content-Type": "application/json"}

    async def open(self) -> None:
        """
        **Coroutine**

        Open an internal `httpx.AsyncClient` session if not already open.
        This is automatically handled during context manager entry.
        """
        if self._reentrance_count == 0:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        self._reentrance_count += 1

    async def close(self) -> None:
        """
        **Coroutine**

        Close the internal `httpx.AsyncClient` session.

        Raises an exception if called without a matching open.
        """
        if self._reentrance_count < 1:
            raise Exception("HttpClient close called before any open — unmatched close detected.")

        self._reentrance_count -= 1
        if self._reentrance_count == 0 and self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "HttpClient":
        """Support `async with` usage for automatic session management."""
        await self.open()
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback_object: Optional[TracebackType]
    ) -> None:
        """Close the session upon context exit."""
        if self._client is not None:
            await self._client.__aexit__(exception_type, exception_value, traceback_object)
        await self.close()

    async def request(
        self,
        method: str,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP request with the given method and endpoint.

        **Parameters**

        - ***method*** (`str`) —
          HTTP method (e.g., `"GET"`, `"POST"`, `"PATCH"`, `"DELETE"`).

        - ***endpoint*** (`str`) —
          API endpoint relative to the configured base URL.

        - ***token*** (`Optional[Sensitive[str]]`) —
          Optional bearer token used for authorization.

        - ***response_encoding*** (`ResponseEncoding`) —
          Determines how the response is parsed.
          Options include: `Json`, `Text`, `Bytes`, `Iterator`.

        - ***kwargs*** (`RequestKwargs`) —
          Additional keyword arguments supported by `httpx`, such as `json`, `params`, or `data`.

        **Response Structure**

        - ***response*** (`Any`) —
          Decoded response object according to the selected encoding:
          - `Json` → Parsed JSON (`dict` or `list`)
          - `Text` → String response body
          - `Bytes` → Raw bytes
          - `Iterator` → Tuple of `(headers, AsyncIterator[bytes])` for streamed data

        **Example Usage:**
        ```python
        async with HttpClient() as client:
            response = await client.request("GET", "models", token=my_token)
            print(response)
        ```
        """
        headers = self._create_headers(token)
        request = self._client.build_request(method, endpoint, headers=headers, **kwargs)
        stream_response = response_encoding == ResponseEncoding.Iterator
        response = await self._client.send(request, stream=stream_response)
        return self._parse_response(response, response_encoding)

    async def get(
        self,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP **GET** request to the given endpoint.

        This is a convenience wrapper for:
        ```python
        await self.request("GET", endpoint, ...)
        ```

        **Parameters**

        - ***endpoint*** (`str`) —
          API path relative to the base URL.

        - ***token*** (`Optional[Sensitive[str]]`) —
          Optional bearer token for authorization.

        - ***response_encoding*** (`ResponseEncoding`) —
          Determines how the response body is decoded:
          `Json`, `Text`, `Bytes`, or `Iterator`.

        - ***kwargs*** (`RequestKwargs`) —
          Additional parameters forwarded to `httpx`, such as:
          - `params` (`dict`) — Query parameters
          - `headers` (`dict`) — Extra headers
          - `timeout` (`float`)
          - `json`, `data` inputs, etc.

        **Returns**

        - Parsed response according to `response_encoding`:
          - `Json`  → `dict` or `list`
          - `Text`  → `str`
          - `Bytes` → `bytes`
          - `Iterator` → `(headers, async iterator over bytes)`

        **Example**
        ```python
        async with HttpClient() as client:
            models = await client.get("models/list", token=my_token)
        ```
        """
        return await self.request("GET", endpoint, token, response_encoding=response_encoding, **kwargs)


    async def post(
        self,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP **POST** request to the given endpoint.

        This is a convenience wrapper around:
        ```python
        await self.request("POST", endpoint, ...)
        ```

        **Parameters**

        - ***endpoint*** (`str`) — API path relative to the base URL.
        - ***token*** (`Optional[Sensitive[str]]`) — Authorization token.
        - ***response_encoding*** (`ResponseEncoding`) — Response decoding mode.
        - ***kwargs*** (`RequestKwargs`) — Additional request arguments such as:
          - `json` (`Any`) — JSON request body
          - `data` (`dict`) — Form data
          - `params` (`dict`) — URL query parameters

        **Returns**

        - The decoded server response according to `response_encoding`.

        **Example**
        ```python
        payload = {"name": "test"}
        async with HttpClient() as client:
            created = await client.post("models/create", json=payload, token=my_token)
        ```
        """
        return await self.request("POST", endpoint, token, response_encoding=response_encoding, **kwargs)


    async def put(
        self,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP **PUT** request to the given endpoint.

        **Parameters**

        - ***endpoint*** (`str`) — Target API path.
        - ***token*** (`Optional[Sensitive[str]]`) — Optional bearer token.
        - ***response_encoding*** (`ResponseEncoding`) — Response parsing strategy.
        - ***kwargs*** (`RequestKwargs`) — Extra arguments passed directly to `httpx`.

        **Returns**

        - Parsed response according to the selected `response_encoding`.

        **Example**
        ```python
        update = {"enabled": True}
        async with HttpClient() as client:
            resp = await client.put("models/update/123", json=update, token=my_token)
        ```
        """
        return await self.request("PUT", endpoint, token, response_encoding=response_encoding, **kwargs)


    async def patch(
        self,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP **PATCH** request to modify fields of an existing resource.

        **Parameters**

        - ***endpoint*** (`str`) — Endpoint relative to the base URL.
        - ***token*** (`Optional[Sensitive[str]]`) — Bearer token for authentication.
        - ***response_encoding*** (`ResponseEncoding`) — Output decoding mode.
        - ***kwargs*** (`RequestKwargs`) — Additional keyword arguments such as:
          - `json` — Patch body
          - `params` — Query parameters

        **Returns**

        - Decoded server response.

        **Example**
        ```python
        patch_data = {"description": "Updated text"}
        async with HttpClient() as client:
            resp = await client.patch("models/modify/123", json=patch_data, token=my_token)
        ```
        """
        return await self.request("PATCH", endpoint, token, response_encoding=response_encoding, **kwargs)


    async def delete(
        self,
        endpoint: str,
        token: Optional[Sensitive[str]] = None,
        *,
        response_encoding: ResponseEncoding = ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send an HTTP **DELETE** request to remove a resource.

        **Parameters**

        - ***endpoint*** (`str`) — Resource path to delete.
        - ***token*** (`Optional[Sensitive[str]]`) — Authorization token.
        - ***response_encoding*** (`ResponseEncoding`) — How to decode the response.
        - ***kwargs*** (`RequestKwargs`) — Additional supported HTTP arguments.

        **Returns**

        - Parsed response (typically JSON or text).

        **Example**
        ```python
        async with HttpClient() as client:
            resp = await client.delete("models/123", token=my_token)
        ```
        """
        return await self.request("DELETE", endpoint, token, response_encoding=response_encoding, **kwargs)


    async def post_multipart(
        self,
        endpoint: str,
        token: Sensitive[str],
        *,
        response_encoding=ResponseEncoding.Json,
        **kwargs: Unpack[RequestKwargs]
    ) -> Any:
        """
        **Coroutine**

        Send a multipart form-data POST request for file uploads.

        **Parameters**

        - ***endpoint*** (`str`) —
          API endpoint relative to the base URL.

        - ***token*** (`Sensitive[str]`) —
          Bearer token used for authorization.

        - ***response_encoding*** (`ResponseEncoding`) —
          Determines how to parse the response. Defaults to JSON.

        - ***kwargs*** —
          Additional request arguments:
          - **data** (`dict`) — Form fields to include.
          - **files** (`dict`) — File-like objects to upload.

        **Response Structure**

        - ***response*** (`Any`) —
          Decoded server response, typically a parsed JSON object.

        **Example Usage:**
        ```python
        files = {"file": open("weights.pt", "rb")}
        async with HttpClient() as client:
            response = await client.post_multipart("upload/model", token=my_token, files=files)
            print(response)
        ```
        """
        headers = {"Authorization": f"Bearer {token.value()}"}
        data = kwargs.get("data", {})
        files = kwargs.get("files", {})
        response = await self._client.request("POST", endpoint, headers=headers, data=data, files=files)
        return self._parse_response(response, response_encoding)

    def _create_headers(self, token: Optional[Sensitive[str]]) -> dict[str, str]:
        """Construct default request headers and include bearer token if available."""
        headers = self._headers.copy()
        if token is not None:
            headers["Authorization"] = f"Bearer {token.value()}"
        return headers

    @staticmethod
    def _parse_response(response: httpx.Response, response_encoding: ResponseEncoding) -> Any:
        """
        Parse an HTTP response based on the configured encoding type.

        Raises detailed exceptions for failed responses.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                method = e.request.method
                url = e.request.url
                status_code = e.response.status_code
                detail = e.response.json()
            except Exception:
                method = e.request.method
                url = e.request.url
                status_code = e.response.status_code
                detail = e.response.text

            message = f"""
                Request failed
                Method: {method}
                URL: {url}
                Status: {status_code}
                Detail: {detail}
            """
            raise Exception(message) from e

        if response_encoding == ResponseEncoding.Bytes:
            return response.content
        if response_encoding == ResponseEncoding.Iterator:
            return response.headers, HttpClient._response_iterator(response)
        if response_encoding == ResponseEncoding.Json:
            return response.json()
        if response_encoding == ResponseEncoding.Text:
            return response.text
        raise ValueError(f"Invalid response encoding: {response_encoding}")

    @staticmethod
    async def _response_iterator(response: Response) -> AsyncGenerator[bytes, None]:
        """Yield streamed response chunks as bytes asynchronously."""
        try:
            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk
        finally:
            await response.aclose()
