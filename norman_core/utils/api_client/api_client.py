import asyncio
from typing import Optional, Union

import httpx
from norman_objects.shared.security.sensitive import Sensitive
from typing_extensions import Unpack

from norman_core._app_config import AppConfig
from norman_core.utils.api_client.objects.request_kwargs import RequestKwargs
from norman_core.utils.api_client.objects.response_encoding import ResponseEncoding


class ApiClient:
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self._client = httpx.AsyncClient(
            base_url=base_url or AppConfig.http.base_url,
            timeout=timeout or AppConfig.http.timeout,
            headers={"Content-Type": "application/json"}
        )

    async def get(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        response = await self._client.get(endpoint, headers=headers, **kwargs)
        return self._parse_response(response, response_encoding)

    async def post(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        response = await self._client.post(endpoint, headers=headers, **kwargs)
        return self._parse_response(response, response_encoding)

    async def put(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        response = await self._client.put(endpoint, headers=headers, **kwargs)
        return self._parse_response(response, response_encoding)

    async def patch(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        response = await self._client.patch(endpoint, headers=headers, **kwargs)
        return self._parse_response(response, response_encoding)

    async def delete(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        response = await self._client.request("DELETE", endpoint, headers=headers, **kwargs)
        return self._parse_response(response, response_encoding)

    async def post_multipart(self, endpoint: str, token: Optional[Sensitive[str]] = None, *, response_encoding = ResponseEncoding.JSON, **kwargs: Unpack[RequestKwargs]):
        headers = self.create_headers(token)

        data = kwargs.get("data", {})
        files = kwargs.get("files", {})
        boundary = "----NormanBoundary"
        content_type = f"multipart/form-data; boundary={boundary}"
        headers["Content-Type"] = content_type

        # Construct multipart payload
        parts: list[Union[str, bytes]] = []
        for key, value in data.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n')
        for filename, (file_obj, file_content_type) in files.items():
            parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{filename}"; filename="{filename}"\r\n'
                f'Content-Type: {file_content_type}\r\n\r\n'
            )
            if hasattr(file_obj, "read"):
                if asyncio.iscoroutinefunction(file_obj.read):
                    parts.append(await file_obj.read())
                else:
                    parts.append(file_obj.read())
            else:
                parts.append(file_obj)
            parts.append(b"\r\n" if isinstance(parts[-1], bytes) else "\r\n")
        parts.append(f"--{boundary}--\r\n")

        content = b""
        for part in parts:
            content += part.encode("utf-8") if isinstance(part, str) else part

        response = await self._client.post(endpoint, headers=headers, content=content)
        return self._parse_response(response, response_encoding)

    def create_headers(self, token: Optional[Sensitive[str]]):
        headers = self._client.headers.copy()
        if token is not None:
            headers["Authorization"] = f"Bearer {token.value()}"
        return headers

    @staticmethod
    def _parse_response(response: httpx.Response, response_encoding: ResponseEncoding):
        response.raise_for_status()

        if response_encoding == ResponseEncoding.JSON:
            return response.json()
        if response_encoding == ResponseEncoding.TEXT:
            return response.text
        if response_encoding == ResponseEncoding.BYTES:
            return response.content
        raise ValueError(f"Invalid response encoding: {response_encoding}")

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)
        return self

    def __repr__(self):
        return f"<Norman.ApiClient base_url={self._client.base_url} closed={self._client.is_closed}>"