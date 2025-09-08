import asyncio
from typing import Optional

from norman_objects.services.invoke.invocation_config import InvocationConfig
from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import HttpClient
from norman_core.utils.api_client.objects.request_kwargs import FileStream


class Invoke:
    @staticmethod
    async def invoke_model(http_client: HttpClient, token: Sensitive[str], invocation_config: InvocationConfig, model_files: Optional[dict[str, FileStream]] = None):
        data = {
            "invocation_config": invocation_config.model_dump_json()
        }

        files = {}
        if model_files:
            for file_name, file_stream in model_files.items():
                if hasattr(file_stream, "read") and asyncio.iscoroutinefunction(file_stream.read):
                    file_stream = await file_stream.read()
                files[file_name] = (file_name, file_stream, "application/octet-stream")

        response = await http_client.post_multipart("invoke/model", token, data=data, files=files)
        return Invocation.model_validate(response)
