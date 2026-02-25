from typing import Optional

from norman_objects.shared.capacity.capacity_usage import CapacityUsage
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class CapacityUsageService(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_capacity_usage(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> list[CapacityUsage]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("persist/capacity/usage/get", token, json=json)
        return TypeAdapter(list[CapacityUsage]).validate_python(response)