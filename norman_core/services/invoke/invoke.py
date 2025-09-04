from norman_objects.services.invoke.invocation_config import InvocationConfig
from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.utils.api_client import ApiClient
from norman_core.utils.api_client.objects.request_kwargs import FileStream


class Invoke:
    @staticmethod
    async def invoke_model(api_client: ApiClient, token: Sensitive[str], invocation_config: InvocationConfig, model_files: dict[str, FileStream] = None):
        data = {
            "invocation_config": invocation_config.model_dump_json()
        }

        files = {
            file_name: (file_stream, "application/octet-stream")
            for file_name, file_stream in (model_files or {}).items()
        } if model_files else {}

        response = await api_client.post_multipart("invoke/model", token, data=data, files=files)
        return Invocation.model_validate(response)
