from typing import Optional

from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class Models:
    @staticmethod
    async def get_models(api_client: ApiClient, token: Sensitive[str] ,request: Optional[GetModelsRequest] = None):
        if request is None:
            request = GetModelsRequest(constraints=None, finished_models=True)
        response = await api_client.post("persist/models/get", token, json=request.model_dump(mode="json"))
        return TypeAdapter(list[Model]).validate_python(response)

    @staticmethod
    async def create_models(api_client: ApiClient, token: Sensitive[str] ,models: list[Model]):
        response = await api_client.post("persist/models/", token, json=TypeAdapter(list[Model]).dump_python(models, mode="json"))
        return TypeAdapter(dict[str, Model]).validate_python(response)

    @staticmethod
    async def upgrade_models(api_client: ApiClient, token: Sensitive[str] ,models: list[Model]):
        response = await api_client.post("persist/models/version", token, json=TypeAdapter(list[Model]).dump_python(models, mode="json"))
        return TypeAdapter(dict[str, Model]).validate_python(response)

    @staticmethod
    async def update_models(api_client: ApiClient, token: Sensitive[str] ,models: list[Model]):
        response = await api_client.patch("persist/models/", token, json=TypeAdapter(list[Model]).dump_python(models, mode="json"))
        return TypeAdapter(dict[str, Model]).validate_python(response)

    @staticmethod
    async def set_active_model(api_client: ApiClient, token: Sensitive[str] ,model_previews: list[ModelPreview]):
        response = await api_client.patch("persist/models/version", token, json=TypeAdapter(list[ModelPreview]).dump_python(model_previews, mode="json"))
        return TypeAdapter(list[ModelPreview]).validate_python(response)

    @staticmethod
    async def delete_models(api_client: ApiClient, token: Sensitive[str] ,constraints: QueryConstraints):
        response: int = await api_client.delete("persist/models/", token, json=constraints.model_dump())
        return response
