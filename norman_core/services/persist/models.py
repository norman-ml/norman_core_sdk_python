from typing import Optional

from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.models.model_projection import ModelProjection
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.versions.model_version_preview import ModelVersionPreview
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Models(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_models(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, Model]:
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/models/get", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    async def get_model_previews(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, ModelPreview]:
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/models/previews/get", token, json=json)
        return TypeAdapter(dict[str, ModelPreview]).validate_python(response)

    async def create_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.post("persist/models", token, json=json)
        return TypeAdapter(list[Model]).validate_python(response)

    async def create_model_projections(self, token: Sensitive[str], model_projections: list[ModelProjection]) -> dict[str, ModelProjection]:
        json = None
        if model_projections is not None:
            json = TypeAdapter(list[ModelProjection]).dump_python(model_projections, mode="json")

        response = await self._http_client.put("persist/models/projections", token, json=json)
        return TypeAdapter(list[ModelProjection]).validate_python(response)

    async def upgrade_model_projections(self, token: Sensitive[str], model_projections: list[ModelProjection]) -> dict[str, ModelProjection]:
        json = None
        if model_projections is not None:
            json = TypeAdapter(list[ModelProjection]).dump_python(model_projections, mode="json")

        response = await self._http_client.post("persist/models/projections", token, json=json)
        return TypeAdapter(list[ModelProjection]).validate_python(response)

    async def set_active_model_versions(self, token: Sensitive[str], model_version_previews: list[ModelVersionPreview]) -> list[ModelVersionPreview]:
        json = None
        if model_version_previews is not None:
            json = TypeAdapter(list[ModelVersionPreview]).dump_python(model_version_previews, mode="json")

        response = await self._http_client.patch("persist/models/version", token, json=json)
        return TypeAdapter(list[ModelVersionPreview]).validate_python(response)

    async def delete_models(self, token: Sensitive[str], constraints: QueryConstraints) -> int:
        json = constraints.model_dump()

        affected_entities_count: int = await self._http_client.delete("persist/models/", token, json=json)
        return affected_entities_count
