from types import TracebackType
from typing import Any, AsyncGenerator
from typing import Optional, Type
from typing_extensions import Unpack

import httpx
from httpx import Response
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton

from norman_core._app_config import AppConfig
from norman_core.clients.objects.request_kwargs import RequestKwargs
from norman_core.clients.objects.response_encoding import ResponseEncoding


class HttpClient(metaclass=Singleton):
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None) -> None:
        self._client = None
        self._open_count = 0

        if base_url is None:
            self._base_url = AppConfig.http.base_url
        else:
            self._base_url = base_url

        if timeout is None:
            self._timeout = AppConfig.http.timeout_seconds
        else:
            self._timeout = timeout

        self._headers = {
            "Content-Type": "application/json"
        }

    async def open(self) -> None:
        if self._open_count == 0:
            await self.close()
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout
            )
        self._open_count += 1

    async def close(self) -> None:
        if self._open_count == 0:
            return

        self._open_count -= 1
        if self._open_count == 0 and self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        await self.open()
        await self._client.__aenter__()
        return self

    async def __aexit__(
            self,
            exception_type: Optional[Type[BaseException]],
            exception_value: Optional[BaseException],
            traceback_object: Optional[TracebackType]
    ) -> None:
        if self._client is not None:
            await self._client.__aexit__(exception_type, exception_value, traceback_object)

        await self.close()

    async def request(self, method: str, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        headers = self._create_headers(token)
        request = self._client.build_request(method, endpoint, headers=headers, **kwargs)

        stream_response = response_encoding == ResponseEncoding.Iterator
        response = await self._client.send(request, stream=stream_response)
        return self._parse_response(response, response_encoding)

    async def get(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        return await self.request("GET", endpoint, token, response_encoding=response_encoding, **kwargs)

    async def post(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        return await self.request("POST", endpoint, token, response_encoding=response_encoding, **kwargs)

    async def put(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        return await self.request("PUT", endpoint, token, response_encoding=response_encoding, **kwargs)

    async def patch(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        return await self.request("PATCH", endpoint, token, response_encoding=response_encoding, **kwargs)

    async def delete(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        return await self.request("DELETE", endpoint, token, response_encoding=response_encoding, **kwargs)

    async def post_multipart(self, endpoint: str, token: Sensitive[str], *, response_encoding = ResponseEncoding.Json, **kwargs: Unpack[RequestKwargs]) -> Any:
        headers = {
            "Authorization": f"Bearer {token.value()}",
        }

        data = kwargs.get("data", {})
        files = kwargs.get("files", {})

        response = await self._client.request(
            "POST",
            endpoint,
            headers=headers,
            data=data,
            files=files
        )
        return self._parse_response(response, response_encoding)

    def _create_headers(self, token: Optional[Sensitive[str]]) -> dict[str, str]:
        headers = self._headers.copy()
        if token is not None:
            headers["Authorization"] = f"Bearer {token.value()}"
        return headers

    @staticmethod
    def _parse_response(response: httpx.Response, response_encoding: ResponseEncoding) -> Any:
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
                f"Request failed\n"
                f"Method: {method}\n"
                f"URL: {url}\n"
                f"Status: {status_code}\n"
                f"Detail: {detail}"
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
        try:
            async for chunk in response.aiter_bytes():
                if chunk is not None and len(chunk) > 0:
                    yield chunk
        finally:
            await response.aclose()
