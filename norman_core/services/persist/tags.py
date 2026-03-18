from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.tags.model_tag import ModelTag
from norman_utils.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Tags(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_tags(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> dict[str, ModelTag]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("persist/tags/user/get", token, json=json)
        return TypeAdapter(dict[str, ModelTag]).validate_python(response)

    async def create_tags(self, token: Sensitive[str], tags: list[ModelTag]) -> list[ModelTag]:
        json = None
        if tags is not None:
            json = TypeAdapter(list[ModelTag]).dump_python(tags, mode="json")

        response = await self._http_client.post("persist/tags", token, json=json)
        return TypeAdapter(list[ModelTag]).validate_python(response)

    async def delete_tags(self, token: Sensitive[str], constraints: QueryConstraints) -> int:
        json = constraints.model_dump(mode="json")

        affected_entities_count: int = await self._http_client.delete("persist/tags/", token, json=json)
        return affected_entities_count
