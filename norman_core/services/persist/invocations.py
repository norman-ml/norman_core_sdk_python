from typing import Optional

from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Invocations(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_invocations(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> dict[str, Invocation]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")
        response = await self._http_client.post("persist/invocations/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)

    async def create_invocations(self, token: Sensitive[str], invocations: list[Invocation]) -> list[Invocation]:
        json = TypeAdapter(list[Invocation]).dump_python(invocations, mode="json")
        response = await self._http_client.post("persist/invocations", token, json=json)
        return TypeAdapter(list[Invocation]).validate_python(response)

    async def create_invocations_by_model_names(self, token: Sensitive[str], model_name_counter: dict[str, int]) -> list[Invocation]:
        response = await self._http_client.post("persist/invocations/by-name", token, json=model_name_counter)
        return TypeAdapter(list[Invocation]).validate_python(response)

    async def get_invocation_history(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> dict[str, Invocation]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")
        response = await self._http_client.post("persist/invocation/history/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)
