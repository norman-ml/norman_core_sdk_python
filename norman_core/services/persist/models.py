from typing import Optional

from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Models(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()
    
    async def get_models(self, token: Sensitive[str], request: Optional[GetModelsRequest] = None) -> dict[str, Model]:
        if request is None:
            request = GetModelsRequest(constraints=None, finished_models=True)
        json = request.model_dump(mode="json")

        response = await self._http_client.post("persist/models/get", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    
    async def create_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.post("persist/models/", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    
    async def upgrade_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.post("persist/models/version", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    
    async def replace_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.patch("persist/models/", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    
    async def set_active_model(self, token: Sensitive[str], model_previews: list[ModelPreview]) -> list[ModelPreview]:
        json = None
        if model_previews is not None:
            json = TypeAdapter(list[ModelPreview]).dump_python(model_previews, mode="json")

        response = await self._http_client.patch("persist/models/version", token, json=json)
        return TypeAdapter(list[ModelPreview]).validate_python(response)

    
    async def delete_models(self, token: Sensitive[str], constraints: QueryConstraints) -> int:
        json = constraints.model_dump()

        affected_entities_count: int = await self._http_client.delete("persist/models/", token, json=json)
        return affected_entities_count
