from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class InvocationFlags(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_invocation_status_flags(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = constraints.model_dump(mode="json") if constraints else None
        response = await self._http_client.post("persist/invocation/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)

    async def get_input_status_flags(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = constraints.model_dump(mode="json") if constraints else None
        response = await self._http_client.post("persist/input/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)

    async def get_output_status_flags(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = constraints.model_dump(mode="json") if constraints else None
        response = await self._http_client.post("persist/output/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
