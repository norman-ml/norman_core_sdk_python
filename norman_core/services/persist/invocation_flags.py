from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class InvocationFlags:
    @staticmethod
    async def get_invocation_status_flags(api_client: ApiClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        response = await api_client.post("/persist/invocation/flags/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return TypeAdapter(dict[str,list[StatusFlag]]).validate_python(response)

    @staticmethod
    async def get_input_status_flags(api_client: ApiClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        response = await api_client.post("/persist/input/flags/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return TypeAdapter(dict[str,list[StatusFlag]]).validate_python(response)

    @staticmethod
    async def get_output_status_flags(api_client: ApiClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        response = await api_client.post("/persist/output/flags/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return TypeAdapter(dict[str,list[StatusFlag]]).validate_python(response)
