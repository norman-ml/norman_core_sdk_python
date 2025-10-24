from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class StatusFlags(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_status_flags(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> dict[str, list[StatusFlag]]:
        json = None
        if constraints is not None:
            json=constraints.model_dump(mode="json")

        response = await self._http_client.post("/persist/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
