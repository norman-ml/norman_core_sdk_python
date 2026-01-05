from norman_objects.shared.models.aggregate_tag import AggregateTag
from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.models.model_projection import ModelProjection
from norman_objects.shared.models.model_tag import ModelTag
from norman_objects.shared.models.model_version_preview import ModelVersionPreview
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter
from typing import Optional

from norman_core.clients.http_client import HttpClient


class Tags(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_user_tags_per_model(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, ModelTag]:
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/tags/user/get", token, json=json)
        return TypeAdapter(dict[str, ModelTag]).validate_python(response)

    async def add_tag(self, token: Sensitive[str], tags: list[ModelTag]) -> list[ModelTag]:
        json = None
        if tags is not None and len(tags) > 0:
            json = TypeAdapter(list[ModelTag]).dump_python(tags, mode="json")

        response = await self._http_client.post("persist/tags", token, json=json)
        return TypeAdapter(list[ModelTag]).validate_python(response)

    async def delete_tag(self, token: Sensitive[str], constraints: QueryConstraints) -> int:
        json = constraints.model_dump(mode="json")

        affected_entities_count: int = await self._http_client.delete("persist/tags/", token, json=json)
        return affected_entities_count
